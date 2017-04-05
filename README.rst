idempotent-sequence
===================

A set of Python classes to declare an idempotent sequence of commands --
a sequence that can be run repeatedly and on success will produce
the same side effects no matter how many times you invoke it.

This is useful when you have a sequence of commands each of which can
fail and you want to keep rerunning the sequence until it succeeds, yet 
you don't want to run previously completed parts again.

See examples under `idemseq/examples`.

::

    $ pip install idempotent-sequence

    $ set IDEMSEQ_SEQUENCE_ID=/tmp/example02.db
    $ export IDEMSEQ_SEQUENCE_ID
    $ set IDEMSEQ_LOG_LEVEL=debug
    $ export IDEMSEQ_LOG_LEVEL

    $ idemseq idemseq.examples.example02:example

    $ idemseq idemseq.examples.example02:example list
    $ idemseq idemseq.examples.example02:example run --dry-run
    $ idemseq idemseq.examples.example02:example run
    $ idemseq idemseq.examples.example02:example reset all

