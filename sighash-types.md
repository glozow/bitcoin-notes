# Sighash types

This note is about signature hashing types.

In src/script/interpreter.h:
```c
/** Signature hash types/flags */
enum
{
    SIGHASH_ALL = 1,
    SIGHASH_NONE = 2,
    SIGHASH_SINGLE = 3,
    SIGHASH_ANYONECANPAY = 0x80,
};

```

In src/script/interpreter.cpp:
```c
template <class T>
uint256 SignatureHash(const CScript& scriptCode, const T& txTo, unsigned int nIn, int nHashType, const CAmount& amount, SigVersion sigversion, const PrecomputedTransactionData* cache)
```

This does the work of selecting which parts of a transaction to hash/serialize and sign.
`int nHashType` is what holds the sighash types.

| sig hash type                                      | inputs (prevouts) | inputs (sequence no) | outputs                  | what we sign                                                                                                           | what can change                      |
|----------------------------------------------------|-------------------|----------------------|--------------------------|------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| SIGHASH_ALL only 0b00000001                        | ALL               | ALL                  | ALL                      | all inputs and outputs in this tx. this is the default.                                                                | NOTHING                              |
| SIGHASH_NONE only 0b00000010                       | ALL               | this input           | NONE                     | all inputs and no outputs                                                                                              | any outputs                          |
| SIGHASH_SINGLE 0b00000011                          | ALL               | this input           | same index as this input | all inputs and one output  (same index as this one)                                                                    | other outputs                        |
| SIGHASH_ALL \| SIGHASH_ANYONECANPAY  0b10000001    | this input        | this input           | ALL                      | one input and all outputs. you and others are contributing  inputs, and all you care is that the outputs don't change. | others' inputs                       |
| SIGHASH_NONE \| SIGHASH_ANYONECANPAY  0b10000010   | this input        | this input           | NONE                     | one input and no outputs you are contributing an input that can be in any tx and can spend to any address(es).         | other inputs and  any of the outputs |
| SIGHASH_SINGLE \| SIGHASH_ANYONECANPAY  0b10000011 | this input        | this input           | same index as this input | one input and one output. you are contributing an input and care about 1 output.                                       | other inputs and other outputs       |
