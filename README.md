# idempotent-sequence

A set of Python classes that provides a way to declare an idempotent sequence of 
commands -- a sequence that can be run repeatedly and on success will produce 
the same side effects no matter how many times you invoke it.

This is useful when you have a sequence of commands each of which can fail and you want
to keep rerunning the sequence until it succeeds, yet you don't want to run previously
completed commands again.

An example from `idemseq/examples/first.py`:
    
    """
    An example that demonstrates all the features of the first version.
    """
    
    import random
    
    from idemseq.idempotent_sequence import CommandSequence
    
    seq = CommandSequence()
    
    
    # Mark a command that needs to run even if it has succeeded before
    @seq.command(run_always=True)
    def greeting():
        print('Hello, world!')
    
    
    # Change the order of commands, defaults to the order in which they are declared
    @seq.command(order=1000)
    def the_last_command():
        print('All is done now!')
    
    
    # Command arguments are injected from invocation context, default values are respected
    @seq.command
    def second(random_number_generator, x=0.5):
        print('Attempting second')
        if random_number_generator() < x:
            raise Exception('Second command randomly failed!')
        print('Second succeeded')
    
    
    # Commands can be given custom names
    @seq.command(name='third')
    def third_command(random_number_generator):
        print('Attempting third')
        if random_number_generator() < 0.5:
            raise Exception('Third command randomly failed')
        print('Third succeeded')
    
    
    if __name__ == '__main__':
        invocation = seq('/tmp/first-example-invocation.db', context=dict(random_number_generator=random.random))
    
        for i in range(5):
            try:
                invocation.run()
            except Exception:
                # We are lazy, let's ignore exceptions for this example
                pass
    
        # If we still haven't succeeded, let's inject a better random number generator --
        # all should surely succeed with this one!
        invocation.run(context=dict(random_number_generator=lambda: 1.0))

An output example for the code above:

    Hello, world!
    Attempting second
    Hello, world!       <-- again because it has run_always=True
    Attempting second   <-- again because apparently it had failed the first time
    Second succeeded
    Attempting third
    Third succeeded
    All is done now!    <-- the last one
    Hello, world!
    Hello, world!
    Hello, world!
    Hello, world!