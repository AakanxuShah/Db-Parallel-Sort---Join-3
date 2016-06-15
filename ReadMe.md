# ReadMe :

## Here, the required task is to build a generic parallel sort and parallel join algorithm.

**1)** Implemented a Python function **ParallelSort()** that takes as input: (1) InputTable stored in
a PostgreSQL database, (2) SortingColumnName the name of the column used to order
the tuples by.

ParallelSort() then sorts all tuples (using five parallelized threads) and
stores the sorted tuples for in a table named OutputTable (the output table name is
passed to the function). The OutputTable contains all the tuple present in InputTable
sorted in ascending order.

**OutputTable** – Name of the table where the output needs to be stored.
openconnection – connection to the database.

**2)** Implement a Python function **ParallelJoin()** that takes as input: (1) InputTable1 and
InputTable2 table stored in a PostgreSQL database, (2) Table1JoinColumn and
Table2JoinColumn that represent the join key in each input table respectively.

ParallelJoin() then joins both InputTable1 and InputTable2 (using five parallelized
threads) and stored the resulting joined tuples in a table named OutputTable (the output
table name is passed to the function).

The schema of OutputTable should be similar to the schema of both InputTable1 and InputTable2 combined.
