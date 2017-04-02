idempotent-sequence
===================

A set of Python classes that provides a way to declare an idempotent sequence of 
commands -- a sequence that can be run repeatedly and on success will produce 
the same side effects no matter how many times you invoke it.

This is useful when you have a sequence of commands (scripts) each of which can 
fail and you want to keep rerunning the sequence until it succeeds, yet 
you don't want to run previously completed parts again.

See examples in `idemseq/examples/`
