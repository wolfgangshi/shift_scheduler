from csp import *

"""
To describe a shift scheduling problem, we must properly define the variables, domains, and constraints.

1. Variables.
   Each shift is considered to be a variable, for example, Monday morning, Wednsday afternoon, and Sunday evening. So there are totally 7*3=21 variables. The possible values that each variable can take on can thus be represented as a list of sets of the staff that are on duty for that particular shift which is denoted by the variable. Var[MondayMorning] = [ [Alice, Bob], [Jennifer, Bob], [Alice, Jennifer] ].

2. Domains.
   As described in the Variable section, a domain of a shift variable can be represented as a list of sets of the staff. Theoretically, if there is a total staff of five, then there are a total of 1 + 5 + 5*4/2 + 5*4*3 / (3*2) + 5 + 1 possible values for each variable. But practically, there must be a certain minimum and maximum number of staff on duty for each shift. So in practice, the number of possible values in the domains can be reduced considerably.

3. Employees.
   Each time an assignment is made, we update the assigned employee's states, which can be used by the constraints. For example, employees have a property called assigned_working_days, which is a seven-element list of 0 or 1s, where 0 of the 1st element denotes the employ rest on Monday, and 1 means there is at least a shift assigned to this employee on Monday. Each time we assign a new Value to a Variable, we update this value, then use it to limit the consecutive working days for an employee.
   The idea is that we can use different properties of employees to achieve the constraints that can be otherwise difficult to be described.

4. Constraints.
   - Unary constraints on shifts. The unary constraints can be applied in a pre-process step to construct an initial stqte of a refined problem . Unary constraints consists of:
     * mininum and maximum number of staff for each shift.
     * one or more staff must be on duty on a particular shift. (e.g. there must be at least one manager on each shift)
     * one or more staff must rest on a particular shift.

   - Employee constraints. There are the main constraints we used to solve this problem.
     * One employee only works one shift a day. Use an employee property workday_assigned_times, which is a list of integers that denotes the time of times an employee has been assigned each day. The constraint should be that for each element in workday_assigned_times the number must not be greater than 1.
     * One employee does not work a morning shift after an evening shift the day before.
     ...
"""

g_weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
g_shifts = ['Morning', 'AfterNoon', 'Evening']
g_shift_names = []
for w in g_weekdays:
    for s in g_shifts:
        g_shift_names.append(w+s)

#print "shift names: %s " % g_shift_names

import itertools
John = ('John', 'Manager')
Joe = ('Joe', 'Manager')
Billy = ('Billy', 'Manager')
Bob = ('Bob', 'Manager')
Christina = ('Christina','Manager')
AA=    ('AA', 'Sales')
BB=    ('BB', 'Sales')
CC=    ('CC', 'Sales')
DD=    ('DD', 'Sales')
EE=    ('EE', 'Sales')
FF=    ('FF', 'Sales')
GG=    ('GG', 'Sales')
HH=    ('HH', 'Sales')
II=    ('II', 'Sales')
JJ=    ('JJ', 'Sales')
KK=    ('KK', 'Sales')
MM=    ('MM', 'Sales')
LL=    ('LL', 'Sales')
NN=    ('NN', 'Sales')
OO=    ('OO', 'Sales')

managers = [John, Joe, Billy, Bob, Christina]
sales = [AA, BB, CC, DD, EE, FF, GG, HH, KK]


class Shift(Variable):
    """

    """
    def __init__(self, name, domain, manager_num=1, sales_num=3, value=None):
        """
        override the __init__ method.
        """
        self._manager_num = manager_num
        self._sales_num = sales_num
        self._domain_value_generator = None
        super(Shift, self).__init__(name, domain, value)

    def copy(self):
        """
        override
        """
        return Shift(self._name, self._domain, self._manager_num, self._sales_num, self._value)

    def get_domain(self):
        """
        override
        """
        if not self._domain_value_generator:
            self._domain_value_generator = self._f()
        return self._domain_value_generator()

    def reduce_domain(self, domain_value):
        """
        override
        """
        self._domain.remove(domain_value)
        self._domain_value_generator = None

    def domain_size(self):
        """
        override
        """
        if not self._domain_value_generator:
            self._domain_value_generator = self._f()
        return len( list( self._domain_value_generator() ))

    def _f(self):
        def _f_1():
            managers = []
            sales = []
            for name, title in self._domain:
                if title == 'Manager':
                    managers.append((name, title,))
                elif title == 'Sales':
                    sales.append((name, title,))
                else:
                    raise Exception('Unknown title: %s for %s' % (title, name))
            manager_iter = itertools.combinations( managers, self._manager_num )
            sales_iter = itertools.combinations( sales, self._sales_num )

            for m in manager_iter:
                for s in sales_iter:
                    print 'yielding'
                    yield m + s

        return _f_1

class Employee(object):
    def __init__(self, name, title):
        self._name = name
        self._title = title


def shifts_csv_problem():
    """
    Initialise and preprocess the shift.
    Variables are 21 different shifts. For each variable there are unary constraints:
    3 > len(value) > 0
    return a dictionary of shift names to possible assignment for each shift.
    """

    variables = []

    for n in g_shift_names:
        variables.append( Shift(n, g_shift_assignments) )

    constraints = []

    def length_limit(val_a, val_b, name_a=None, name_b=None):
        return len(val_a) <= 4 and len(val_a) >= 2

    for n in g_shift_names:
        constraints.append(BinaryConstraint(n, n, length_limit, "1 <= len(%s) <= 3" %n))

    def no_consecutive_shifts(val_a, val_b, name_a=None, name_b=None):
        print "no_consecutive_shifts: %s, %s" %(val_a, val_b)
        return set(val_a).isdisjoint(set(val_b))

    s_names = g_shift_names
    while len(s_names) > 1:
        n1, n2 = tuple(s_names[:2])
        print n1 + "-" + n2
        constraints.append(BinaryConstraint(n1, n2, no_consecutive_shifts, "No employee should be on two consecutive shifts: (%s) and (%s)" % (n1, n2)))
        s_names.pop(0)

    return CSP(constraints, variables)

if __name__ == '__main__':
    #checker = basic_constraint_checker
    #solve_csp_problem(shifts_csv_problem, checker, verbose=True)
    shift = Shift('MondayMorning', managers[:1] + sales[:4])
    assert('MondayMorning' == shift.get_name())
    assert(4 == shift.domain_size())

    ## test Shift.get_domain()
    domain_values = []
    for d in shift.get_domain():
        domain_values.append(d)
    print 'dv %s' % (domain_values)

    assert([
        (John, AA, BB, CC),
        (John, AA, BB, DD),
        (John, AA, CC, DD),
        (John, BB, CC, DD),
        ] == domain_values )

    ## test Shift.reduce_domain()
    print 'shift: %s' % shift
    shift.reduce_domain( AA )
    assert(1 == shift.domain_size())

    domain_values = []
    for d in shift.get_domain():
        domain_values.append(d)
    print 'dv after remove "AA" %s' % (domain_values)
    assert( [(John, BB, CC, DD)] == domain_values )

    ## test Shift.copy()
    shift = Shift('MondayMorning', managers[:1] + sales[:4])
    new_shift = shift.copy()
    shift.reduce_domain( AA )
    assert(1 == shift.domain_size())
    assert(4 == new_shift.domain_size())
