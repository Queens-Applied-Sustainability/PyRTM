

if __name__ == '__main__':
    print('Running a sample SBDART session...')
    from pyrtm.sbdart.wrapper import SBDART
    from pyrtm.sbdart.config import EXAMPLE_INPUTS
    s = SBDART(cleanup=False)
    s.atmosphere.update(EXAMPLE_INPUTS)
    s.go()
