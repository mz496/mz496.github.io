// Author:
// Title:

#ifdef GL_ES
precision mediump float;
#endif

uniform vec2 u_resolution;
uniform vec2 u_mouse;
uniform float u_time;

/*
Exact distance to cubic bezier curve by computing roots of the derivative(s)
to isolate roots of a fifth degree polynomial and Halley's Method to compute them.
Inspired by https://www.shadertoy.com/view/4sXyDr and https://www.shadertoy.com/view/ldXXWH
See also my approximate version:
https://www.shadertoy.com/view/lsByRG
*/
const float eps = .000005;
const float zoom = 1.;
const float dot_size=.005;
const vec4 point_col=vec4(1,1,0,1);
const int halley_iterations = 8;
const float PI = 3.14159;

//lagrange positive real root upper bound
//see for example: https://doi.org/10.1016/j.jsc.2014.09.038
float upper_bound_lagrange5(float a0, float a1, float a2, float a3, float a4){

	vec4 coeffs1 = vec4(a0,a1,a2,a3);

	vec4 neg1 = max(-coeffs1,vec4(0));
	float neg2 = max(-a4,0.);

	const vec4 indizes1 = vec4(0,1,2,3);
	const float indizes2 = 4.;

	vec4 bounds1 = pow(neg1,1./(5.-indizes1));
	float bounds2 = pow(neg2,1./(5.-indizes2));

	vec2 min1_2 = min(bounds1.xz,bounds1.yw);
	vec2 max1_2 = max(bounds1.xz,bounds1.yw);

	float maxmin = max(min1_2.x,min1_2.y);
	float minmax = min(max1_2.x,max1_2.y);

	float max3 = max(max1_2.x,max1_2.y);

	float max_max = max(max3,bounds2);
	float max_max2 = max(min(max3,bounds2),max(minmax,maxmin));

	return max_max + max_max2;
}

//lagrange upper bound applied to f(-x) to get lower bound
float lower_bound_lagrange5(float a0, float a1, float a2, float a3, float a4){

	vec4 coeffs1 = vec4(-a0,a1,-a2,a3);

	vec4 neg1 = max(-coeffs1,vec4(0));
	float neg2 = max(-a4,0.);

	const vec4 indizes1 = vec4(0,1,2,3);
	const float indizes2 = 4.;

	vec4 bounds1 = pow(neg1,1./(5.-indizes1));
	float bounds2 = pow(neg2,1./(5.-indizes2));

	vec2 min1_2 = min(bounds1.xz,bounds1.yw);
	vec2 max1_2 = max(bounds1.xz,bounds1.yw);

	float maxmin = max(min1_2.x,min1_2.y);
	float minmax = min(max1_2.x,max1_2.y);

	float max3 = max(max1_2.x,max1_2.y);

	float max_max = max(max3,bounds2);
	float max_max2 = max(min(max3,bounds2),max(minmax,maxmin));

	return -max_max - max_max2;
}

vec2 parametric_cub_bezier(float t, vec2 p0, vec2 p1, vec2 p2, vec2 p3){
	vec2 a0 = (-p0 + 3. * p1 - 3. * p2 + p3);
	vec2 a1 = (3. * p0  -6. * p1 + 3. * p2);
	vec2 a2 = (-3. * p0 + 3. * p1);
	vec2 a3 = p0;

	return (((a0 * t) + a1) * t + a2) * t + a3;
}

void sort_roots3(inout vec3 roots){
	vec3 tmp;

	tmp[0] = min(roots[0],min(roots[1],roots[2]));
	tmp[1] = max(roots[0],min(roots[1],roots[2]));
	tmp[2] = max(roots[0],max(roots[1],roots[2]));

	roots=tmp;
}

void sort_roots4(inout vec4 roots){
	vec4 tmp;

	vec2 min1_2 = min(roots.xz,roots.yw);
	vec2 max1_2 = max(roots.xz,roots.yw);

	float maxmin = max(min1_2.x,min1_2.y);
	float minmax = min(max1_2.x,max1_2.y);

	tmp[0] = min(min1_2.x,min1_2.y);
	tmp[1] = min(maxmin,minmax);
	tmp[2] = max(minmax,maxmin);
	tmp[3] = max(max1_2.x,max1_2.y);

	roots = tmp;
}

float eval_poly5(float a0, float a1, float a2, float a3, float a4, float x){

	float f = ((((x + a4) * x + a3) * x + a2) * x + a1) * x + a0;

	return f;
}

//halley's method
//basically a variant of newton raphson which converges quicker and has bigger basins of convergence
//see http://mathworld.wolfram.com/HalleysMethod.html
//or https://en.wikipedia.org/wiki/Halley%27s_method
float halley_iteration5(float a0, float a1, float a2, float a3, float a4, float x){

	float f = ((((x + a4) * x + a3) * x + a2) * x + a1) * x + a0;
	float f1 = (((5. * x + 4. * a4) * x + 3. * a3) * x + 2. * a2) * x + a1;
	float f2 = ((20. * x + 12. * a4) * x + 6. * a3) * x + 2. * a2;

	return x - (2. * f * f1) / (2. * f1 * f1 - f * f2);
}

float halley_iteration4(vec4 coeffs, float x){

	float f = (((x + coeffs[3]) * x + coeffs[2]) * x + coeffs[1]) * x + coeffs[0];
	float f1 = ((4. * x + 3. * coeffs[3]) * x + 2. * coeffs[2]) * x + coeffs[1];
	float f2 = (12. * x + 6. * coeffs[3]) * x + 2. * coeffs[2];

	return x - (2. * f * f1) / (2. * f1 * f1 - f * f2);
}

// Modified from http://tog.acm.org/resources/GraphicsGems/gems/Roots3And4.c
// Credits to Doublefresh for hinting there
int solve_quadric(vec2 coeffs, inout vec2 roots){

    // normal form: x^2 + px + q = 0
    float p = coeffs[1] / 2.;
    float q = coeffs[0];

    float D = p * p - q;

    if (D < 0.){
		return 0;
    }
    else if (D > 0.){
		roots[0] = -sqrt(D) - p;
		roots[1] = sqrt(D) - p;

		return 2;
    }
}

//From Trisomie21
//But instead of his cancellation fix i'm using a newton iteration
int solve_cubic(vec3 coeffs, inout vec3 r){

	float a = coeffs[2];
	float b = coeffs[1];
	float c = coeffs[0];

	float p = b - a*a / 3.0;
	float q = a * (2.0*a*a - 9.0*b) / 27.0 + c;
	float p3 = p*p*p;
	float d = q*q + 4.0*p3 / 27.0;
	float offset = -a / 3.0;
	if(d >= 0.0) { // Single solution
		float z = sqrt(d);
		float u = (-q + z) / 2.0;
		float v = (-q - z) / 2.0;
		u = sign(u)*pow(abs(u),1.0/3.0);
		v = sign(v)*pow(abs(v),1.0/3.0);
		r[0] = offset + u + v;

		//Single newton iteration to account for cancellation
		float f = ((r[0] + a) * r[0] + b) * r[0] + c;
		float f1 = (3. * r[0] + 2. * a) * r[0] + b;

		r[0] -= f / f1;

		return 1;
	}
	float u = sqrt(-p / 3.0);
	float v = acos(-sqrt( -27.0 / p3) * q / 2.0) / 3.0;
	float m = cos(v), n = sin(v)*1.732050808;

	//Single newton iteration to account for cancellation
	//(once for every root)
	r[0] = offset + u * (m + m);
    r[1] = offset - u * (n + m);
    r[2] = offset + u * (n - m);

	vec3 f = ((r + a) * r + b) * r + c;
	vec3 f1 = (3. * r + 2. * a) * r + b;

	r -= f / f1;

	return 3;
}

// Modified from http://tog.acm.org/resources/GraphicsGems/gems/Roots3And4.c
// Credits to Doublefresh for hinting there
int solve_quartic(vec4 coeffs, inout vec4 s){

	float a = coeffs[3];
	float b = coeffs[2];
	float c = coeffs[1];
	float d = coeffs[0];

    /*  substitute x = y - A/4 to eliminate cubic term:
	x^4 + px^2 + qx + r = 0 */

    float sq_a = a * a;
    float p = - 3./8. * sq_a + b;
    float q = 1./8. * sq_a * a - 1./2. * a * b + c;
    float r = - 3./256.*sq_a*sq_a + 1./16.*sq_a*b - 1./4.*a*c + d;

	int num;

	/* doesn't seem to happen for me */
    //if(abs(r)<eps){
	//	/* no absolute term: y(y^3 + py + q) = 0 */

	//	vec3 cubic_coeffs;

	//	cubic_coeffs[0] = q;
	//	cubic_coeffs[1] = p;
	//	cubic_coeffs[2] = 0.;

	//	num = solve_cubic(cubic_coeffs, s.xyz);

	//	s[num] = 0.;
	//	num++;
    //}
    {
		/* solve the resolvent cubic ... */

		vec3 cubic_coeffs;

		cubic_coeffs[0] = 1.0/2. * r * p - 1.0/8. * q * q;
		cubic_coeffs[1] = - r;
		cubic_coeffs[2] = - 1.0/2. * p;

		solve_cubic(cubic_coeffs, s.xyz);

		/* ... and take the one real solution ... */

		float z = s[0];

		/* ... to build two quadric equations */

		float u = z * z - r;
		float v = 2. * z - p;

		if(u > -eps){
			u = sqrt(abs(u));
		}
		else{
			return 0;
		}

		if(v > -eps){
			v = sqrt(abs(v));
		}
		else{
			return 0;
		}

		vec2 quad_coeffs;

		quad_coeffs[0] = z - u;
		quad_coeffs[1] = q < 0. ? -v : v;

		num = solve_quadric(quad_coeffs, s.xy);

		quad_coeffs[0]= z + u;
		quad_coeffs[1] = q < 0. ? v : -v;

		vec2 tmp=vec2(1e38);
		int old_num=num;

		num += solve_quadric(quad_coeffs, tmp);
        if(old_num!=num){
            if(old_num == 0){
                s[0] = tmp[0];
                s[1] = tmp[1];
            }
            else{//old_num == 2
                s[2] = tmp[0];
                s[3] = tmp[1];
            }
        }
    }

    /* resubstitute */

    float sub = 1./4. * a;

	/* single halley iteration to fix cancellation */
	for(int i=0;i<4;i+=2){
		if(i < num){
			s[i] -= sub;
			s[i] = halley_iteration4(coeffs,s[i]);

			s[i+1] -= sub;
			s[i+1] = halley_iteration4(coeffs,s[i+1]);
		}
	}

    return num;
}

//Sign computation is pretty straightforward:
//I'm solving a cubic equation to get the intersection count
//of a ray from the current point to infinity and parallel to the x axis
//Also i'm computing the intersection count with the tangent in the end points of the curve
float cubic_bezier_sign(vec2 uv, vec2 p0, vec2 p1, vec2 p2, vec2 p3){

	float cu = (-p0.y + 3. * p1.y - 3. * p2.y + p3.y);
	float qu = (3. * p0.y - 6. * p1.y + 3. * p2.y);
	float li = (-3. * p0.y + 3. * p1.y);
	float co = p0.y - uv.y;

	vec3 roots = vec3(1e38);
	int n_roots = solve_cubic(vec3(co/cu,li/cu,qu/cu),roots);

	int n_ints = 0;

	for(int i=0;i<3;i++){
		if(i < n_roots){
			if(roots[i] >= 0. && roots[i] <= 1.){
				float x_pos = -p0.x + 3. * p1.x - 3. * p2.x + p3.x;
				x_pos = x_pos * roots[i] + 3. * p0.x - 6. * p1.x + 3. * p2.x;
				x_pos = x_pos * roots[i] + -3. * p0.x + 3. * p1.x;
				x_pos = x_pos * roots[i] + p0.x;

				if(x_pos < uv.x){
					n_ints++;
				}
			}
		}
	}

	vec2 tang1 = p0.xy - p1.xy;
	vec2 tang2 = p2.xy - p3.xy;

	vec2 nor1 = vec2(tang1.y,-tang1.x);
	vec2 nor2 = vec2(tang2.y,-tang2.x);

	if(p0.y < p1.y){
		if((uv.y<=p0.y) && (dot(uv-p0.xy,nor1)<0.)){
			n_ints++;
		}
	}
	else{
		if(!(uv.y<=p0.y) && !(dot(uv-p0.xy,nor1)<0.)){
			n_ints++;
		}
	}

	if(p2.y<p3.y){
		if(!(uv.y<=p3.y) && dot(uv-p3.xy,nor2)<0.){
			n_ints++;
		}
	}
	else{
		if((uv.y<=p3.y) && !(dot(uv-p3.xy,nor2)<0.)){
			n_ints++;
		}
	}

	if(n_ints==0 || n_ints==2 || n_ints==4){
		return 1.;
	}
	else{
		return -1.;
	}
}

float cubic_bezier_dis(vec2 uv, vec2 p0, vec2 p1, vec2 p2, vec2 p3){

	//switch points when near to end point to minimize numerical error
	//only needed when control point(s) very far away
	#if 0
	vec2 mid_curve = parametric_cub_bezier(.5,p0,p1,p2,p3);
	vec2 mid_points = (p0 + p3)/2.;

	vec2 tang = mid_curve-mid_points;
	vec2 nor = vec2(tang.y,-tang.x);

	if(sign(dot(nor,uv-mid_curve)) != sign(dot(nor,p0-mid_curve))){
		vec2 tmp = p0;
		p0 = p3;
		p3 = tmp;

		tmp = p2;
		p2 = p1;
		p1 = tmp;
	}
	#endif

	vec2 a3 = (-p0 + 3. * p1 - 3. * p2 + p3);
	vec2 a2 = (3. * p0 - 6. * p1 + 3. * p2);
	vec2 a1 = (-3. * p0 + 3. * p1);
	vec2 a0 = p0 - uv;

    //compute polynomial describing distance to current pixel dependent on a parameter t
	float bc6 = dot(a3,a3);
	float bc5 = 2.*dot(a3,a2);
	float bc4 = dot(a2,a2) + 2.*dot(a1,a3);
	float bc3 = 2.*(dot(a1,a2) + dot(a0,a3));
	float bc2 = dot(a1,a1) + 2.*dot(a0,a2);
	float bc1 = 2.*dot(a0,a1);
	float bc0 = dot(a0,a0);

	bc5 /= bc6;
	bc4 /= bc6;
	bc3 /= bc6;
	bc2 /= bc6;
	bc1 /= bc6;
	bc0 /= bc6;

    //compute derivatives of this polynomial

	float b0 = bc1 / 6.;
	float b1 = 2. * bc2 / 6.;
	float b2 = 3. * bc3 / 6.;
	float b3 = 4. * bc4 / 6.;
	float b4 = 5. * bc5 / 6.;

	vec4 c1 = vec4(b1,2.*b2,3.*b3,4.*b4)/5.;
	vec3 c2 = vec3(c1[1],2.*c1[2],3.*c1[3])/4.;
	vec2 c3 = vec2(c2[1],2.*c2[2])/3.;
	float c4 = c3[1]/2.;

	vec4 roots_drv = vec4(1e38);

	int num_roots_drv = solve_quartic(c1,roots_drv);
	sort_roots4(roots_drv);

	float ub = upper_bound_lagrange5(b0,b1,b2,b3,b4);
	float lb = lower_bound_lagrange5(b0,b1,b2,b3,b4);

	vec3 a = vec3(1e38);
	vec3 b = vec3(1e38);

	vec3 roots = vec3(1e38);

	int num_roots = 0;

	//compute root isolating intervals by roots of derivative and outer root bounds
    //only roots going form - to + considered, because only those result in a minimum
	if(num_roots_drv==4){
		if(eval_poly5(b0,b1,b2,b3,b4,roots_drv[0]) > 0.){
			a[0]=lb;
			b[0]=roots_drv[0];
			num_roots=1;
		}

		if(sign(eval_poly5(b0,b1,b2,b3,b4,roots_drv[1])) != sign(eval_poly5(b0,b1,b2,b3,b4,roots_drv[2]))){
            if(num_roots == 0){
				a[0]=roots_drv[1];
				b[0]=roots_drv[2];
                num_roots=1;
            }
            else{
            	a[1]=roots_drv[1];
				b[1]=roots_drv[2];
                num_roots=2;
            }
		}

		if(eval_poly5(b0,b1,b2,b3,b4,roots_drv[3]) < 0.){
            if(num_roots == 0){
                a[0]=roots_drv[3];
                b[0]=ub;
                num_roots=1;
            }
            else if(num_roots == 1){
                a[1]=roots_drv[3];
                b[1]=ub;
                num_roots=2;
            }
            else{
                a[2]=roots_drv[3];
                b[2]=ub;
                num_roots=3;
            }
		}
	}
	else{
		if(num_roots_drv==2){
			if(eval_poly5(b0,b1,b2,b3,b4,roots_drv[0]) < 0.){
				num_roots=1;
				a[0]=roots_drv[1];
				b[0]=ub;
			}
			else if(eval_poly5(b0,b1,b2,b3,b4,roots_drv[1]) > 0.){
				num_roots=1;
				a[0]=lb;
				b[0]=roots_drv[0];
			}
			else{
				num_roots=2;

				a[0]=lb;
				b[0]=roots_drv[0];

				a[1]=roots_drv[1];
				b[1]=ub;
			}

		}
		else{//num_roots_drv==0
			vec3 roots_snd_drv=vec3(1e38);
			int num_roots_snd_drv=solve_cubic(c2,roots_snd_drv);

			vec2 roots_trd_drv=vec2(1e38);
			int num_roots_trd_drv=solve_quadric(c3,roots_trd_drv);
			num_roots=1;

			a[0]=lb;
			b[0]=ub;
		}

        //further subdivide intervals to guarantee convergence of halley's method
		//by using roots of further derivatives
		vec3 roots_snd_drv=vec3(1e38);
		int num_roots_snd_drv=solve_cubic(c2,roots_snd_drv);
		sort_roots3(roots_snd_drv);

		int num_roots_trd_drv=0;
		vec2 roots_trd_drv=vec2(1e38);

		if(num_roots_snd_drv!=3){
			num_roots_trd_drv=solve_quadric(c3,roots_trd_drv);
		}

		for(int i=0;i<3;i++){
			if(i < num_roots){
				for(int j=0;j<3;j+=2){
					if(j < num_roots_snd_drv){
						if(a[i] < roots_snd_drv[j] && b[i] > roots_snd_drv[j]){
							if(eval_poly5(b0,b1,b2,b3,b4,roots_snd_drv[j]) > 0.){
								b[i]=roots_snd_drv[j];
							}
							else{
								a[i]=roots_snd_drv[j];
							}
						}
					}
				}
				for(int j=0;j<2;j++){
					if(j < num_roots_trd_drv){
						if(a[i] < roots_trd_drv[j] && b[i] > roots_trd_drv[j]){
							if(eval_poly5(b0,b1,b2,b3,b4,roots_trd_drv[j]) > 0.){
								b[i]=roots_trd_drv[j];
							}
							else{
								a[i]=roots_trd_drv[j];
							}
						}
					}
				}
			}
		}
	}

	float min_squared_dist = 1e38;
    float min_t = 1e38;

    //compute roots with halley's method

	for(int i=0;i<3;i++){
		if(i < num_roots){
			roots[i] = .5 * (a[i] + b[i]);

            for(int j=0;j<halley_iterations;j++){
				roots[i] = halley_iteration5(b0,b1,b2,b3,b4,roots[i]);
            }


            //compute squared distance to nearest point on curve
			roots[i] = clamp(roots[i],0.,1.);
            vec2 eval_root = parametric_cub_bezier(roots[i],p0,p1,p2,p3);
			vec2 to_curve = uv - eval_root;
            float to_curve_squared_dist = dot(to_curve,to_curve);
            if (to_curve_squared_dist < min_squared_dist) {
				min_squared_dist = min(min_squared_dist,to_curve_squared_dist);
                min_t = roots[i];
            }
		}
	}

	return min_t;
    //return sqrt(min_squared_dist);
}

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

float hue2rgb(float f1, float f2, float hue) {
    if (hue < 0.0)
        hue += 1.0;
    else if (hue > 1.0)
        hue -= 1.0;
    float res;
    if ((6.0 * hue) < 1.0)
        res = f1 + (f2 - f1) * 6.0 * hue;
    else if ((2.0 * hue) < 1.0)
        res = f2;
    else if ((3.0 * hue) < 2.0)
        res = f1 + (f2 - f1) * ((2.0 / 3.0) - hue) * 6.0;
    else
        res = f1;
    return res;
}

vec3 hsl2rgb(vec3 hsl) {
    vec3 rgb;

    if (hsl.y == 0.0) {
        rgb = vec3(hsl.z); // Luminance
    } else {
        float f2;

        if (hsl.z < 0.5)
            f2 = hsl.z * (1.0 + hsl.y);
        else
            f2 = hsl.z + hsl.y - hsl.y * hsl.z;

        float f1 = 2.0 * hsl.z - f2;

        rgb.r = hue2rgb(f1, f2, hsl.x + (1.0/3.0));
        rgb.g = hue2rgb(f1, f2, hsl.x);
        rgb.b = hue2rgb(f1, f2, hsl.x - (1.0/3.0));
    }
    return rgb;
}

vec3 hsl2rgb(float h, float s, float l) {
    return hsl2rgb(vec3(h, s, l));
}


float ramp(float d, float t, float sgn, float D) {
    /*if (t == 0. && sgn > 0.) {
        return 1.;
    }*/

    return clamp(-(1./(2.*(t*sgn*D))) * d + 0.5, 0., 1.);
}

void make_bezier(vec2 uv, vec2 p0, vec2 p1, vec2 p2, vec2 p3,
                 out float t, out float d, out float sgn, inout float dots) {
    // What value of 0<=t<=1 is the closest point on the bezier?
    t = cubic_bezier_dis(uv,p0,p1,p2,p3);
    // What is the point you get when you plug t into the bezier?
    vec2 eval_t0 = parametric_cub_bezier(t,p0,p1,p2,p3);
    // Vector from current frag point to eval_t0; distance to point on bezier with param t
    vec2 to_t0 = uv - eval_t0;
    vec2 p3_uv = uv - p3;
    vec2 p3_uv_norm = p3_uv / sqrt(dot(p3_uv,p3_uv));
    vec2 p3_p2 = p2 - p3;
    vec2 p3_p2_norm = p3_p2 / sqrt(dot(p3_p2,p3_p2));
    float angle_p3_uv = atan(p3_uv_norm.y,p3_uv_norm.x);
    float angle_p3_p2 = atan(p3_p2_norm.y,p3_p2_norm.x);
    float bezier_sgn0 = cubic_bezier_sign(uv,p0,p1,p2,p3);
    if (bezier_sgn0 > 0. && angle_p3_p2 < angle_p3_uv + eps && angle_p3_uv < angle_p3_p2 + PI) {
        sgn = 1.;
    } else {
        sgn = -1.;
    }
    d = sqrt(dot(to_t0,to_t0));
    dots = min(dots,distance(p0,uv) - dot_size);
	dots = min(dots,distance(p1,uv) - dot_size);
    dots = min(dots,distance(p2,uv) - dot_size);
	dots = min(dots,distance(p3,uv) - dot_size);
}

vec4 layer(vec4 a, vec4 b) {
    vec3 Ca = a.rgb;
    vec3 Cb = b.rgb;
    float ao = a.a + b.a * (1. - a.a);
    vec3 Co = (Ca * a.a + Cb * (1. - a.a));
    return vec4(Co.rgb, ao);
    //return foreground * foreground.a + background * (1.0 - foreground.a);
}

//void mainImage(out vec4 fragColor, in vec2 fragCoord){
void main() {

    vec4 fragCoord = gl_FragCoord;
    vec2 iResolution = u_resolution;
    vec2 iMouse = u_mouse;
    float iTime = u_time;

	float border=2./iResolution.x;

	vec2 uv = fragCoord.xy / iResolution.xy;
	uv-=.5;
	uv.y *= iResolution.y / iResolution.x;

	vec2 mouse = iMouse.xy / iResolution.xy;
	mouse-=.5;
	mouse.y *= iResolution.y / iResolution.x;

	border*=zoom;
	uv *= zoom;
	mouse *= zoom;

	//float t0 = mod(iTime*2.+1.5,24.*3.1416);


    //mouse condition copied from mattz (https://www.shadertoy.com/view/4dyyR1)
    /*if(max(iMouse.x, iMouse.y) > 20.){
        p0=vec2(-.3,-.1);
        p1=mouse;
        p2=vec2(.1,-.2);
        p3=vec2(.2,.15);
    }*/

    // M = 0.2
    // f(d, t): rgba(hsv2rgb(360*t), 1.-d)


    float dots = 1e38;

    vec2 p0 = vec2(0.430,0.450);
    vec2 p1 = vec2(0.1, 0.5);
    vec2 p2 = vec2(0.320,0.180);
    vec2 p3 = vec2(-0.150,0.060);
    float t0;
    float d0;
    float sgn0;
	make_bezier(uv, p0, p1, p2, p3, t0, d0, sgn0, dots);





    /*
    vec2 p4 = p3;
    vec2 p5 = p4 + (p3-p2);
    vec2 p6 = vec2(-0.3, -0.4);
    vec2 p7 = vec2(-0.400,-0.330);
    float t1;
    float d1;
    float sgn1;
	make_bezier(uv, p4, p5, p6, p7, t1, d1, sgn1, dots);
    */





    float h1 = 0.928;
    float h2 = 0.154;
    float h3 = 0.5;
    float s = .7;
    float l = .7;
    float D = 0.212;

    //float d = min(min(1e38,d0),d1);
    float d = min(1e38,d0);
    float sgn;
    if (sgn0 > 0.) {// || sgn1 > 0.) {
        sgn = 1.;
    } else {
        sgn = -1.;
    }
    float t = t0;
    /*
    if (t1 > 0. && d1 < D) {
        t = 0.5 + t1/2.;
    } else {
        t = t0/2.;
    }*/

    vec4 col = vec4(hsl2rgb(vec3(h2,s,l)),ramp(d,t,sgn,D));
    vec4 colB = vec4(hsl2rgb(vec3(h1,s,l)),0.984);

	//iq's sd color scheme
    // Color regions as a function of t, d
    //col = color(t0, d0, sgn0);
    // f(0) = (h1+h2)/2, f(D) = h2, f(-D) = h1
    // hue = d*(h2-h1)/(2D) + (h1+h2)/2
        //float hue = clamp(d0*(h1-h2)/(2.*D) + (h1+h2)/2., h2, h1);
        // (d=0,a=.5) (d=D,a=1)
        //col = vec4(hsl2rgb(vec3(h1,s,mix(0.75,0.7,1.-exp(-10.*d0)))),1);

    // Color the +/- regions differently
	//vec3 col = vec3(1.0) - sgn*vec3(0.1,0.4,0.7);
    // Color a shadow around the curve
    //col *= 1.0 - exp(-8.0 * d0);
    // Color the contour
	//col *= 0.8 + 0.2*cos(480.0*d0);
    // Color in the curve itself using a stepdown from white at small values of d0
	//col = mix(col, vec4(1.0), 1.0-smoothstep(0.0,0.005,abs(d0)));
	// Color in dots
    //col = mix(point_col,col,smoothstep(0.,border,dots));

    //gl_FragColor = col;
	gl_FragColor = layer(col, colB);
}
