# Add Python implementation of Minisketch

Review Club notes


1. **How are finite field elements represented in Python? How do we perform additions, subtractions, multiplications, and divisions on them? How are polynomials with finite field coefficients represented in Python?**

- In `GF2Ops`, finite fields of size `2^field_size` have elements represented as integers. Since `GF(2^field_size)` is isomorphic to `Z_2[x] / (f)` for some polynomial of degree `field_size`, we can interpret the integers as polynomials where the nth bit is the coefficient for `x^{n-1}`.
Each field is determined by the `field_size` - there's an array `GF2_MODULI` of the irreducible polynomials in `Z_2[x]` degrees 2 to 64.
You can grab the nth degree irreducible polynomial by indexing `GF2_MODULI[n]` (first 2 elements are `None` since there are no irreducible polynomials of degree 0 or 1).

- Addition is simply bitwise xor, not exposed in `GF2Ops` class.

- Multiplication (x, y): For each bit in y (from LSB to MSB), add x if the bit = 1, then multiply by 2. Equivalent to adding y copies of x.
Multiplication by 2 (`mul2` function) keeps product within the field size by subtracting modulus if it exceeds it.

- Division (aka multiplying by multiplicative inverse): interesting part is `inv` which finds the multiplicative inverse of x in `GF(2^field_size)`.
The inverse must exist because x is an element of a field, which also means we're guaranteed gcd(x, modulus) = 1.
The gcd of x and modulus can be expressed as `x*t1 + modulus*t2 = 1 mod modulus`. Euclidean GCD algo can do this quickly.
Since the gcd is 1, we have `1 = x*t1 + modulus*t2 = x*t1` (since `modulus*anything = 0 mod modulus`).

2. **Imagine Alice and Bob have sets {a,b,c,d,f} and {b,d,e,f} respectively, where the variables represent distinct non-zero 8-bit field elements. Assume that Alice knows ahead of time that the (symmetric) difference between those two sets is not more than 3. Alice is going to send a sketch of her elements to Bob, so that Bob can learn the differences. How many bits will her sketch be in size? Looking at add, what field elements will that sketch consist of?**

- For reconciling c=3 different b=8-bit elements, sketch size is supposed to be bc = 24 bits(???).

- The `serialized_size` function also seems to return `self.capacity * self.field_size` bits.

3. **Following the same example, Bob will compute a sketch over his own elements, and combine it with the sketch received from Alice. What field elements will that combined sketch contain? Noting that it only contains odd powers, how will Bob restore the even ones (see decode)? Would this work if we weren’t using power-of-two fields?**

- Since the polynomials are over a finite field with a characteristic 2, `a + a = 0` for every `a` in the field and thus `(x + y)^2 = x^2 + y^2`.

- This makes it possible to compute all even syndromes of the sketch from the odd syndromes since every even is some `s(2i) = x^{2i} + y^{2i} + ... = (x + y + ...)^{2i} = si^2`

4. **The next step is converting the power sums to a polynomial using the Berlekamp-Massey. What does this algorithm do for us?**

- It finds the polynomnial (determined by coefficients) that generates the the syndromes.a minimal polynomial L (its coefficients `l_0 ... l_n`) s.t. `S(M)*L` = the power sums.

- This entails solving a system of n linear equations... Berlekamp-Massey does this faster.

5. **The final, and most complicated step to recovering the set of differences is finding the roots of the obtained polynomial. To do so, we first verify that the obtained nth degree polynomial actually has n distinct roots. It relies on the property that (x^(fieldsize) - x) has every field element exactly once as root. How does that let us test if the polynomial is fully factorizable into n roots? Why is this test necessary?**

- A n-degree polynomial can have at most n roots. It _may_ have fewer roots that are repeated (note n-degree polynomial with unique roots is synonymous with having n roots). 

- This is important because our set `{m_1 ... m_n}` is derived from the roots of the polynomial. The Berklekamp Trace Algorithm also requires this I believe. 

- For every finite field of order q, the polynomial `X^q - X` has all q elements of the finite field as its roots exactly once, so it's factorizable into `(X - e_1)(X - e_2)(X - e_3)...(X - e_q)`. If another polynomial has unique roots, `X^q - X` must be a multiple of it.

- The `poly_find_roots` function does this by first making the polynomial monic (leading coefficient = 1), then checks that the polynomial `x^{2^field_size} = x mod poly` which is the same as `x^{2^field_size} - x = 0 mod poly`. And note that, since it's monic, this should be exactly x.

6. To actually find the roots, the Berlekamp Trace Algorithm is used. It uses the trace function `t(x) = x + x^2 + x^4 + ... + x^(fieldsize/2)` which maps every element of a field of size `2^n` to 0 or 1. In our 8-bit field that means `t(x) = x + x^2 + x^4 + x^8 + x^16 x^32 + x^64 + x^128`. This means that for any non-zero field element p, `tr(p*x)` also has this property, and every choice of p will map a different subset of field elements to 0 (and the others to 1). How is this property used to recursively split the polynomial into smaller and smaller ones?

- From the paper, interesting property of the trace function is it's a `F_2`-linear mapping.

- The gcd of the trace and the polynomial is a polynomial with roots = poly and the roots shared between trace and poly.
So you recurse on two parts: (1) gcd (after you make it monic) and (2) poly divided by gcd (which has the other roots).
