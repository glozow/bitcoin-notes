# Policy

[Policy](https://github.com/bitcoin/bitcoin/blob/master/src/policy/policy.h), sometimes also referred to as "standardness," is a collection of validation rules that Bitcoin Core applies to transactions _in addition to consensus_.

## In policy.h

### Script Verification Flags
```
STANDARD_SCRIPT_VERIFY_FLAGS = MANDATORY_SCRIPT_VERIFY_FLAGS |
                                                             SCRIPT_VERIFY_DERSIG |
                                                             SCRIPT_VERIFY_STRICTENC |
                                                             SCRIPT_VERIFY_MINIMALDATA |
                                                             SCRIPT_VERIFY_NULLDUMMY |
                                                             SCRIPT_VERIFY_DISCOURAGE_UPGRADABLE_NOPS |
                                                             SCRIPT_VERIFY_CLEANSTACK |
                                                             SCRIPT_VERIFY_MINIMALIF |
                                                             SCRIPT_VERIFY_NULLFAIL |
                                                             SCRIPT_VERIFY_CHECKLOCKTIMEVERIFY |
                                                             SCRIPT_VERIFY_CHECKSEQUENCEVERIFY |
                                                             SCRIPT_VERIFY_LOW_S |
                                                             SCRIPT_VERIFY_WITNESS |
                                                             SCRIPT_VERIFY_DISCOURAGE_UPGRADABLE_WITNESS_PROGRAM |
                                                             SCRIPT_VERIFY_WITNESS_PUBKEYTYPE |
                                                             SCRIPT_VERIFY_CONST_SCRIPTCODE |
                                                             SCRIPT_VERIFY_TAPROOT |
                                                             SCRIPT_VERIFY_DISCOURAGE_UPGRADABLE_TAPROOT_VERSION |
                                                             SCRIPT_VERIFY_DISCOURAGE_OP_SUCCESS |
                                                             SCRIPT_VERIFY_DISCOURAGE_UPGRADABLE_PUBKEYTYPE;
```
### Size


### Fees

`minrelaytxfee` is a static minimum set by nodes. They won't relay transactions with a fee lower than 1000 sat/KvByte.

`mempoolminfee` is the minimum fee for inclusion in mempool, which changes based on what transactions are in the mempool.
Naturally, this is defined by the lowest-fee transaction in the mempool it's full.
