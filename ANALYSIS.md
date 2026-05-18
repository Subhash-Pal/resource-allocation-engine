# Algorithm Comparison

## Greedy allocation

The greedy allocator sorts requests by priority and start time, then picks the highest-scoring currently available technician for each one.

Strengths:

- Very fast and simple to explain
- Good when requests arrive one-by-one in real time
- Easy to debug because each decision is local

Weaknesses:

- Can consume a flexible technician too early
- May reduce overall coverage when later requests have fewer feasible resources

## Optimal batch allocation

The batch allocator uses dynamic programming to maximize the total score across the whole request set. It treats unassignment as an allowed choice, so it only assigns a request when doing so improves the global plan.

Strengths:

- Better global score on tightly constrained scenarios
- Protects scarce multi-skill resources for the requests where they matter most
- Produces stronger comparison metrics for coverage and overall plan quality

Weaknesses:

- More computationally expensive than greedy
- Best suited to batch planning or short planning windows rather than continuous streaming dispatch

## What I learned

The main difference shows up when resource flexibility is uneven. If one technician can cover several request types and another can cover only one, a greedy algorithm often spends the versatile person first because that choice looks best locally. The batch optimizer can see the whole board and reserve that resource for a later request that would otherwise go uncovered.

In practice, the two approaches can work together:

- Use greedy for very fast live dispatch
- Re-run the batch optimizer periodically for planning windows or what-if analysis
