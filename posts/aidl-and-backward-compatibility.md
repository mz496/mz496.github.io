---
title: AIDL and backward incompatibility
description: Warning, silent failures ahead
date: 2020-12-21
tags:
  - code
layout: layouts/post.njk
---

For anyone who has ever defined an interface in the Android Interface Description Language (AIDL) you may naturally wonder: As a service owner vending a client interface or SDK, what happens when I add, remove, or rename a method? How does versioning work, and how do my clients know about new versions?

After two years hacking on an Android Open Source Project (AOSP)-based device, here are my hard-won learnings on AIDL and backward incompatibility (read: 15-20 hours spent digging into mysterious bugs)!

**Note: Everything here is based off of SDK version 26.**

Let's pull in the [Android SDK docs on AIDL](https://developer.android.com/guide/components/aidl) to take a first stab at this. As of 2020 December 21, they read:

> *Caution:* Any changes that you make to your AIDL interface after your first release must remain backward compatible in order to avoid breaking other applications that use your service. That is, because your .aidl file must be copied to other applications in order for them to access your service's interface, you must maintain support for the original interface.

This is a helpful mental model for those new to AIDL: Each of your *N* clients builds with a copy of the aar when they want to talk to your service apk. The aar(s) and apk all build with the same AIDL interface, which compiles down to a stub Java interface that client and service in turn compile against.

In other words, AIDL is the glue that abstracts away all the inter-process communication (IPC) between the client and the service.

But on the topic of backward incompatibility, it basically just says "don't release backward incompatible changes." Here's a list of other things it does *not* do, which I'll dive into individually:
1. define what constitutes a backward incompatible change
2. what happens if you do release a backward incompatible change
3. what guardrails prevent you from releasing a backward incompatible change
4. how clients know whether you've released an SDK change, backward incompatible or not

Oh and no hate to the Android SDK team. AIDL makes IPC super easy, and in many ways, I've come to really appreciate both the design and development experience on AOSP :)

## What constitutes a backward incompatible change?

I wouldn't be asking this question if it weren't at least somewhat against conventional wisdom, which says that removing methods or changing method signatures via renaming or changing parameters are backward incompatible.

In AIDL, the answer is all of the above, but also **reordering methods and adding methods anywhere that isn't the end of the file.**

[Stack Overflow will tell you the same thing,](https://stackoverflow.com/a/35634603) but I'll try to explain *why* this is the case.

We discussed earlier that AIDL gets compiled down to Java, and the devil is in the details of how that compilation happens. Most illustrative is just to look at the compiled code. For an AIDL interface like this:

```java
// IClientInterface.aidl
interface IClientInterface {
    int foo(in int number);
    int bar(in int number, in String name);
    void baz(in int number, in String name);
}
```
it would get compiled down to something like this:
```java
// IClientInterface.java
public interface IClientInterface extends IInterface {
    int foo(int number) throws RemoteException;
    void bar(int number, String name) throws RemoteException;
    void baz(int number, String name) throws RemoteException;

    public abstract static class Stub extends Binder implements IClientInterface {
        static final int TRANSACTION_foo = 1;
        static final int TRANSACTION_bar = 2;
        static final int TRANSACTION_baz = 3;

        // Use IClientInterface.Stub.asInterface(binder) to talk to the service
        public static IClientInterface asInterface(IBinder obj) { ... }
        // ...

        public onTransact(int code, Parcel data, Parcel reply, int flags) throws RemoteException {
            // ...
            switch(code) {
            case 1:
                // ...
                int _result = this.foo(_arg0);
                // ...
            case 2:
                // ...
                int _result = this.bar(_arg0, _arg1);
                // ...
            case 3:
                // ...
                this.baz(_arg0, _arg1);
                // ...
            case 1598968902:
                reply.writeString(descriptor);
            default:
                return super.onTransact(code, data, reply, flags);
        }
    }
    private static class Proxy implements IBodyTaskModelService {
        // implementations of {foo, bar, baz}
        // that call onTransact(TRANSACTION_{foo, bar, baz}, ...) respectively
    }
}
```
For now I'll draw attention to the fact that **each interface method gets a transaction ID depending on its order in the file,** which means that anything that changes the original order will cause issues for clients if they're using an old version of the interface:

(picture)

## What happens if you do release a backward incompatible change?

If you're lucky: Android SDK will probably loudly complain via a crash in internal code when trying to deserialize arguments of the wrong type. For example, trying to interpret `readInt()` bytes as if they were the result of `readString()` sounds pretty messy. ([It's native JNI code, which is outside the scope of this post (and my understanding), but hopefully the idea is clear.](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/master/core/java/android/os/Parcel.java#2407))

If you're unlucky: Silent disaster! 🤯

### Silent failure mode 1: Your client calls interface method A but gets back results for interface method B
Around November 2019, I made what I thought was a backward-compatible change to my service and client SDK. Except it wasn't; I inserted a new interface method into the middle of the AIDL file.

I then sank 10+ hours into debugging why a client was getting a null result back for a service implementation that never returns null. In my case, the **E**xpected client method `E()` had no arguments, but the **A**ctual method call received on the service was `A(arg0)`, which had one argument. Even though my client SDK did a client-side check to never call `A(arg0)` with a null `arg0`, the service still received it with a null `arg0`. This broke service-side assumptions and returned invalid results.

To see how that was possible, let's add back some context to the compiled AIDL interface:
```java
            case 1:
                data.enforceInterface(descriptor);
                int _result = this.foo(_arg0);
                // ... write _result to reply Parcel ...
                return true;
            case 2:
                data.enforceInterface(descriptor);
                int _arg0 = data.readInt();
                int _arg1 = data.reddInt();
                int _result = this.bar(_arg0, _arg1);
                // ... write _result to reply Parcel ...
                return true;
```
Say the service releases a change deleting `foo` (`case 1`). A call to `foo` from the client would then be interpreted on the service as `bar`, which occupies `case 2` above but now occupies `case 1`. We established this in the previous section.

The nefarious bit is when the call is actually made -- there is no association between parameters and method names at all, just good faith within the AIDL compiler that the transaction number still matches the corresponding method signature implied by the deserialization logic. In the example above, this causes `_arg1` to read as something undefined (probably 0 in practice).

Note `enforceInterface` only checks the class name to make sure the call is coming from the right class, but not the right method.

### Silent failure mode 2: Your client call can go MIA
Around November 2020, I spent 5+ hours debugging why the paper trail for a particular AIDL call ended at the client. To be continued...

### Stable AIDL
By the way, Android 10 introduces the concept of Stable AIDL. The docs appear to be aimed at developers working directly with the SDK internals (I hesitate to use the p-word as I find it overused, but Android "platform" developers) rather than app developers, but it does contain some [references to adding interface methods to the end of the file only.](https://source.android.com/devices/architecture/aidl/stable-aidl#versioning-interfaces).

