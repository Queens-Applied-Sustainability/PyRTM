PROG =	smarts295

OBJS =  smarts295.o

FC = f90
FFLAGS = -O3
LDFLAGS =

LIBS =

ifeq ($(FC), ifort)
	FFLAGS = -fast
endif

$(PROG): $(OBJS)
	$(FC) $(LDFLAGS) -o $@ $(OBJS) $(LIBS)

smarts295.o:  smarts295.f

clean:
	rm -f $(PROG) $(OBJS) *.mod

