# Why does CLEANSTACK need to be used with P2SH and WITNESS?

TLDR: P2SH scriptPubKeys are in the form

```
OP_HASH160 <20B hash> OP_EQUAL
```

A scriptSig must provide a redeemScript that hashes to the value in the `<20B hash>`.

In a P2SH, we actually execute two scripts:

1. We push the script to the stack, hash it, and check that it matches the script hash given in the scriptPubKey.

2. We run the script itself.

After the first execution, in a valid P2SH, we always have the script left on the stack, so it won't be clean.
However, after the second execution, we're at the end of script verification, so we expect to have a clean stack.

Before P2SH was activated, this type of scriptPubKey could still be a valid spending condition
(as is the case with all soft forks). In fact, this spending condition would essentially boil down to
"Pay to Preimage of this hash" so the corresponding scriptSig would simply need to provide the value
for which the OP_HASH160 image is equal to those 20 bytes.

Enforcing CLEANSTACK in a situation like this means that the preimage needs to be size 1.
However, P2SH scriptSigs don't need to be size 1, so this script would be invalid before P2SH but valid after P2SH.
This makes P2SH not backwards-compatible (aka a hard fork).

```
+-------------+---------------------------------------------------+---------------------------------------------------------------+
|             | Pre-P2SH Execution                                | P2SH Execution                                                |
+-------------+---------------------------------------------------+---------------------------------------------------------------+
| no          | 1. Push scriptSig onto the stack.                 | 1. Push scriptSig onto the stack.                             |
| CLEANSTACK  | Top item is redeemScript.                         | Top item is redeemScript.                                     |
|             | 2. EvalScript(scriptPubKey), i.e. check preimage. | 2. EvalScript(scriptPubKey), i.e. check preimage.             |
|             |                                                   | 3. EvalScript(redeemScript): Execute the "script" in P2SH.    |
+-------------+---------------------------------------------------+---------------------------------------------------------------+
| yes         | 1. Push scriptSig onto the stack.                 | 1. Push scriptSig onto the stack.                             |
| CLEANSTACK  | Top item is redeemScript.                         | Top item is redeemScript.                                     |
|             | 2. EvalScript(scriptPubKey), i.e. check preimage. | 2. EvalScript(scriptPubKey), i.e. check preimage.             |
|             | 3. Fail if anything other than OP_TRUE is left    | DON'T check for CLEANSTACK here.                              |
|             | (i.e., preimage size > 1).                        | 3. EvalScript(redeemScript): Execute the "script" in P2SH,    |
|             |                                                   | possibly consuming items that are on the stack from scriptSig |
|             |                                                   | 4. Fail if there's anything left on the stack.                |
+-------------+---------------------------------------------------+---------------------------------------------------------------+
```

## Example: P2SH 2-of-3 multisig


A P2SH 2-of-3 multisig has:

* scriptPubKey: `OP_HASH160 <20B hash> OP_EQUAL`

* scriptSig: `0 <sig1> <sig2> <redeemScript>`

* redeemScript: `OP_2 <pubkey1> <pubkey2> <pubkey3> 3 OP_CHECKMULTISIG>`

```
+---------------------------------------------------+--------------------------------------------------------+
| Pre-P2SH Execution                                | P2SH Execution                                         |
+---------------------------------------------------+--------------------------------------------------------+
| 1. Push scriptSig onto the stack.                 | 1. Push scriptSig onto the stack.                      |
|                                                   |                                                        |
| stack:                                            | stack:                                                 |
| <redeemScript>                                    | <redeemScript>                                         |
| <sig2>                                            | <sig2>                                                 |
| <sig1>                                            | <sig1>                                                 |
| 0                                                 | 0                                                      |
|                                                   |                                                        |
|                                                   |                                                        |
| 2. EvalScript(scriptPubKey), i.e. check preimage. | 2. EvalScript(scriptPubKey), i.e. check preimage.      |
|                                                   | OP_HASH160(redeemScript) must be equal to the hash.    |
| stack:                                            |                                                        |
| OP_TRUE                                           | stack:                                                 |
| <sig2>                                            | OP_TRUE                                                |
| <sig1>                                            | <sig2>                                                 |
| 0                                                 | <sig1>                                                 |
|                                                   | 0                                                      |
|                                                   |                                                        |
|                                                   |                                                        |
| 3. CLEANSTACK: There are 4 items on the stack.    | 2. EvalScript(redeemScript), i.e. run the script.      |
|                                                   |                                                        |
|                                                   | stack:                                                 |
|                                                   | OP_TRUE (after OP_CHECKMULTISIG succeeds)              |
|                                                   |                                                        |
|                                                   |                                                        |
|                                                   | 3. CLEANSTACK: There is 1 item left on the stack.      |
|                                                   | Success                                                |
+---------------------------------------------------+--------------------------------------------------------+

```

Credit: I stole dis from jnewbery hoho