# MMALS-CAL for a 12-Year-Old

Imagine a team that solves puzzles. Some team members are good at shapes, some at numbers, and some at pictures. The MMALS mycelial network is the messenger that helps send each puzzle to useful specialists.

But even a good team needs a referee. MMALS-CAL asks four questions:

1. Did the team learn this kind of puzzle?
2. Did it recognize what kind of puzzle this is?
3. Is its confidence rule still fresh for this kind of puzzle?
4. Is there one clear answer, or should the team say, "I am not sure yet"?

To build the confidence rule, the referee keeps a separate practice box. It looks at how surprised the team was by the correct answers. The 90% conformal quantile is like a line drawn so that about 90% of those surprise scores are below it.

For a new puzzle, every answer that is not too surprising goes into a candidate set. One candidate can allow ACTION. Several candidates produce NO_DECISION. Saying "I am not sure" is better than pretending to know.

In CORe50, the system could cover the true answer about 90% of the time only by keeping about 29 possible labels out of 50. That is honest, but not precise enough to act automatically in most cases.
