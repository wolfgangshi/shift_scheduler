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

print "shift names: %s " % g_shift_names

import itertools
g_employee_names = ['Alice', 'Bob', 'John', 'Joe', 'Christina']
g_shift_assignments = []
for i in xrange( len(g_employee_names) ):
    g_shift_assignments += itertools.combinations(g_employee_names, i)

class Shift(Variable):
    """

    """
#    def __init__(self, name, domain, value=None):
#        super(self.__class__, self).__init__(name, domain, value)

    def set_value(self, value):
        self._value = value
        for employee in value:
            employee.shift_assigned(shift)

    def index(self):
        """
        return an integer which is the current shift's index in the g_shift_names
        """
        return g_shift_names.index( self._name )

    def weekday(self):
        """
        return the weekday of the current shift as an integer index of the
        weekdays list.
        """
        pass

class Employee(object):
    def __init__(self, name):
        self._name = name
        self._shifts = [0]*21

    def shift_assigned(self, shift):
        index = shift.index()
        self._shifts[index] = 1

    def is_one_shift_a_day(self):
        print "Empleoy %s shifts: %s" %(self._name, self._shifts)
        s = self._shifts
        while s:
            if reduce(lambda a,b: a+b, s[:3]) > 1:
                return False
            s = s[3:]
        return True

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

#    def no_consecutive_shifts(val_a, val_b, name_a=None, name_b=None):
#        print "no_consecutive_shifts: %s, %s" %(val_a, val_b)
#        return set(val_a).isdisjoint(set(val_b))

#    s_names = g_shift_names
#    while len(s_names) > 1:
#        n1, n2 = tuple(s_names[:2])
#        print n1 + "-" + n2
#        constraints.append(BinaryConstraint(n1, n2, no_consecutive_shifts, "No employee should be on two consecutive shifts: (%s) and (%s)" % (n1, n2)))
#        s_names.pop(0)

    def one_shift_a_day(val_a, val_b, name_a=None, name_b=None):
        for e in val_a:
            if not e.is_one_shift_a_day():
                return False
        return True

    for n in g_shift_names:
        constraints.append(BinaryConstraint(n, n, one_shift_a_day, "One shift a day"))

    return CSP(constraints, variables)

if __name__ == '__main__':
    checker = basic_constraint_checker
    solve_csp_problem(shifts_csv_problem, checker, verbose=True)
