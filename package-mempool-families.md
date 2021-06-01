# Mempool Policy for Packages

## Background

Each mempool policy has information on its ancestors and descendants in the
mempool.  This speeds up some operations (selecting which transactions to
include in a block and which to evict for low feerates) and slows down others
(adding and removing transactions).

We have ancestor/descendant limits as part of our mempool policy with the goal
of constraining the maximum computation needed for such operations. If seeing a
conflicting transaction in a block causes us to remove a transaction with
10,000 descendants in the mempool, we waste a lot of resources. Attackers can
trigger these on purpose as well.

The ancestor/descendant limits are: no transaction can have more than 25 (or
user config) or 101KvB of ancestors + descendants.  Note that this doesn't mean
there aren't families larger than 25, since it doesn't include co-parents
(ancestor-of-descendant) or siblings (descendant-of-ancestor).

For example, a transaction might only have 24 descendants, but each of those
descendants may have 23 other ancestors:

<img src="./images/large_mempool_family.jpg" width="500">

The important part here is that these policies are imperfect heuristics
intended to limit computational complexity of mempool operations.

### Implementation Details for Calculating Ancestor/Descendant Limits

The function `CalculateMemPoolAncestors()` does most of the work here.  It does
something like this:

- Find all unconfirmed parents: for each input, see if it spends a mempool
   transaction.  Use this list as `staged_ancestors`. From here, we'll process
all unconfirmed ancestors.

- Process transactions from `staged_ancestors`: make sure the tx meets
   ancestor and descendant limits by calculating the count and vsize with
ancestors and descendants.

- Put any in-mempool parents into the `staged_ancestors` list.


## Ancestor / Descendant Limits for Packages

As one may expect, it becomes more difficult to enforce these policies when
validating packages. These examples should illustrate why.
Limiting packages to size 2 also doesn't do much to limit the complexity.

<img src="./images/package_mempool_examples.jpg" width="1000">

We want to be able to validate multiple transactions on top of the mempool, but also avoid these scenarios:

- We underestimate the ancestors/descendants during package validation and end up with extremely
  complex families in our mempool (potentially a DoS vector).
- We expend an unreasonable amount of resources calculating everyone's ancestors and descendants
  during package validation.
