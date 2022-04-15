---
title: AIDL and backward incompatibility
description: Pitfalls when updating AIDL client/service interfaces for Android
date: 2020-12-21
tags:
  - post
  - code
---

If you're an Android developer with a general understanding of the purpose and use of the Android Interface Description Language (AIDL) in interprocess communication, this is for you!

## Quick primer on AIDL and the problem

My main motivation for writing this is to raise big warning flags that I wish I knew before I dropped 15-20 hours looking into issues related to AIDL.

Let's first make sure we're on the same page regarding what AIDL is according to the [Android SDK docs](https://developer.android.com/guide/components/aidl), retrieved 17 Jan 2021:

> It allows you to define the programming interface that both the client and service agree upon in order to communicate with each other using interprocess communication (IPC). On Android, one process cannot normally access the memory of another process. So to talk, they need to decompose their objects into primitives that the operating system can understand, and marshall the objects across that boundary for you. The code to do that marshalling is tedious to write, so Android handles it for you with AIDL.

One common pattern I saw in my time hacking away on an Android Open Source Project (AOSP)-based device is that this usually lends itself pretty well to team boundaries, similar to microservices in the web world. For example, a team might own one service *S* (APKs) and its associated client library (AARs). The client library is then compiled with other services *S2*, *S3*, etc. that would use AIDL under the hood to talk to the service.

![AIDL intro](/static/img/aidl-intro.png)

One question that immediately arises: **How does AIDL handle backward incompatible changes?** This is of particular interest if backward incompatibilities affect other teams, as it did while I was working on one tiny sliver of a ~100-strong apps & services team.

Further down in the Android SDK docs, we see:

> *Caution:* Any changes that you make to your AIDL interface after your first release must remain backward compatible in order to avoid breaking other applications that use your service. That is, because your .aidl file must be copied to other applications in order for them to access your service's interface, you must maintain support for the original interface.

This basically says "don't release backward incompatible changes." Here's a list of other things it does *not* do, which I'll dive into individually:
1. [define what constitutes a backward incompatible change](#what-constitutes-a-backward-incompatible-change%3F)
2. [what happens if you do release a backward incompatible change](#what-happens-if-you-do-release-a-backward-incompatible-change%3F)
3. [what guardrails prevent you from releasing a backward incompatible change](#what-guardrails-prevent-you-from-releasing-a-backward-incompatible-change%3F)

Oh and no hate to the Android SDK. AIDL makes IPC super easy, and in many ways, I've come to really appreciate both the design and development experience on AOSP :)

## What constitutes a backward incompatible change?

Conventional wisdom says that backward incompatible changes include:
* removing methods
* changing method signatures via renaming the method or changing parameters

In AIDL, backward incompatible changes include all of the above *plus the following*:
* reordering methods
* adding methods anywhere that isn't the end of the file

[Stack Overflow will tell you the same thing,](https://stackoverflow.com/a/35634603) but I'll try to explain *why* this is the case.

AIDL gets compiled down to Java so that other apps can actually use it, and the devil is in the details of how that compilation happens. Most illustrative is just to look at the compiled code. For an AIDL interface like this:

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
    private static class Proxy implements IClientInterface {
        // implementations of {foo, bar, baz}
        // that call onTransact(TRANSACTION_{foo, bar, baz}, ...) respectively
    }
}
```

Since the [Android SDK docs on AIDL](https://developer.android.com/guide/components/aidl) already describe how to use this generated code, I'll draw attention to these two points:
* A client SDK plays two roles: expose an interface for clients (to compile with) and the host to agree upon (build against to supply implementation). The backward incompatibilities I'm describing arise from differing versions on the host (S) and the "client" (itself a service, S2).
* Each interface method gets a transaction ID depending on its order in the file. This is why there are issues if you change the original order of the methods.

Here's an example of what happens in a normal case:

![Happy case AIDL](/static/img/aidl-happy.png)

And here's an example of what happens when a client gets a different version with methods reordered in the .aidl file:

![Reordering AIDL methods](/static/img/aidl-reordering.png)

## What happens if you do release a backward incompatible change?

If you're lucky: Android SDK will probably loudly complain via a crash in internal code when trying to deserialize arguments of the wrong type. For example, trying to interpret `readInt()` bytes as if they were the result of `readString()` sounds pretty messy. ([It's native JNI code, which is outside the scope of this post (and my understanding), but hopefully the idea is clear.](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/master/core/java/android/os/Parcel.java#2407))

If you're unlucky: Silent disaster! 🤯

I personally debugged two of these silent failure modes, which I'll describe below:
* Client expects result for calling synchronous (i.e. not `oneway`) method *E*, but the actual result were as if it called method *A*
* Client expects result for calling asynchronous (i.e. `oneway`) method *E*, but the service never receives it

I'm sure one could reason about other failure modes, but I'll just focus on what I had personal experience with.

### Silent failure mode 1: Your client expects results for E but actually gets results for A

Around November 2019, as a service owner, I made what I thought was a backward-compatible change to my service and client SDK. Except it wasn't; I inserted a new interface method into the middle of the AIDL file. This caused a client to suddenly start receiving null for a service implementation that never returns null.

The generalized case is when a client method gets interpreted differently on the service because the transaction IDs have been reassigned. In my case, the **E**xpected client method `E()` had no arguments, but the **A**ctual method call received on the service was `A(arg0)`, which had one argument. Even though I had explicitly written a client-side check in the SDK to never call `A(arg0)` with a null `arg0`, the service still received it with a null `arg0`. This broke service-side assumptions and returned invalid results.

![Adding methods to AIDL interface](/static/img/aidl-adding.png)

To see how that was possible at the code level, let's add back some context to the compiled AIDL interface:
```java
// older client SDK
            case 1:
                data.enforceInterface(descriptor);
                int _result = this.foo(_arg0);
                // ... write _result to reply Parcel ...
                return true;
```
Say we release a change adding a new method to the interface, `hi(int, int)`, and a user of the client SDK (let's call them a customer) doesn't upgrade to it. This means the customer's generated code stays the same, but the newest version that the service is using looks like this:
```java
// newest client SDK
            case 1:
                data.enforceInterface(descriptor);
                int _arg0 = data.readInt();
                int _arg1 = data.readInt();
                int _result = this.hi(_arg0, _arg1);
                // ... write _result to reply Parcel ...
                return true;
            case 2:
                data.enforceInterface(descriptor);
                int _result = this.foo(_arg0);
                // ... write _result to reply Parcel ...
                return true;
```

When the client calls `foo`, it's received on the service as `hi`, no questions asked -- there is no association between parameters and method names at all, just good faith within the AIDL compiler that the transaction number still matches the corresponding method signature implied by the deserialization logic. This also causes the nonexistent `_arg1` (from the customer's perspective) to read as something undefined, probably 0 in practice.

Note `enforceInterface` only checks the class name to make sure the call is coming from the right class, but not the right method. We fixed this by rolling back the service change since there were many potentially affected clients.

### Silent failure mode 2: Your client call can go MIA
Around November 2020, I was investigating why the paper trail for an AIDL call ended at the client: existing logging normally appeared on the client right before calling and on the service right after receiving, but this time, none of the service logging showed up.

This time, I was the client, and an upstream dependency removed an AIDL method. This caused the default transaction ID case to kick in, which neither triggers a service method call (since it's been removed) nor any indication that something has gone wrong (that I know of).

I don't fully understand [the default behavior of onTransact according to the Binder documentation](https://developer.android.com/reference/android/os/Binder#onTransact(int,%20android.os.Parcel,%20android.os.Parcel,%20int)), but one thing was clear: Android internals even affect the way traditional backward incompatibilities fail!

![Deleting methods from AIDL interface](/static/img/aidl-deleting.png)

To see how this happened at the code level, it's also in the first snippet in these lines, almost unassuming enough to be an afterthought. A transaction ID that has no match will fall through to this case:
```java
            default:
                return super.onTransact(code, data, reply, flags);
```

We fixed this by rolling forward, since my team at the time was working with an old version of our upstream vendor, whereas other device teams had already started building the new version.

## What guardrails prevent you from releasing a backward incompatible change?

There are no Android guardrails that I know of with my very limited understanding of AIDL and Android overall. A few ideas for some manual solutions:
* **Instrumented tests or a test client integration that devs use to gate code changes.** These require upfront investment when it can be tempting to offload all tests to a manual QA team, but in my opinion, they are very much worth it. Without these, QA would frequently get completely blocked by show-stopping bugs that would essentially make an entire team's use cases untestable.
* **Releasing client library changes first and asking clients to upgrade before making service changes.** This was a typical practice in my org and likely a typical industry practice as well. By surfacing potential dangers earlier, this reduced blast radius to singular clients since if something broke, individual clients would roll back instead of the service change affecting everyone at once.

### Stable AIDL
Android 10 introduces the concept of [Stable AIDL](https://source.android.com/devices/architecture/aidl/stable-aidl). The docs appear to be aimed at developers working directly with the SDK internals (for example, forking from AOSP?) rather than app developers, but it does contain some [references to adding interface methods to the end of the file only.](https://source.android.com/devices/architecture/aidl/stable-aidl#versioning-interfaces) So I have to give Google credit where it's due.

## Final thoughts

My experience with Android can be summed up in the sentence, "Abstractions are great until they break and you have to un-abstract them to figure out what's going on." I've recently undergone a relatively large switch to a deploy & staging team, and I hope to expand this space with more learnings as I come across them 🧐
