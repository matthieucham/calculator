if __name__ == "__main__":
    import timeit

    for expr in ['5*(2+4)-2*-2^5+1/8*8-2']:
        loop_nb = 10000
        print('time for calc with ShuntingYard algo (%s) looped %d times' % (expr, loop_nb))
        print(timeit.repeat("calc('%s', ShuntingYardEvaluator)" % expr,
                            setup="from calc import calc, ShuntingYardEvaluator", number=loop_nb, repeat=5))
        print('time for calc with PrecedenceClimbing algo (%s) looped %d times' % (expr, loop_nb))
        print(timeit.repeat("calc('%s', PrecedenceClimbingEvaluator)" % expr,
                            setup="from calc import calc, PrecedenceClimbingEvaluator",
                            number=loop_nb, repeat=5))
