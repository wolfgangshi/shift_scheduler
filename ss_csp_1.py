from csp import *

weight_by_title = {'Manager': 100, 'Sales': 1}

class Employee(Variable):
    def __init__(self, name, title, domain, value=None):
        self._name = name
        self._title = title
        self._value = value
        self._domain = self._weight(domain)

    def get_title(self):
        return self._title

    def _weight(self, domain):
        new_domain = set([])
        weight = weight_by_title[self._title]
        for d in domain:
            weighted = tuple(map(lambda x: x * weight, d))
            new_domain.add( weighted )
        return list(new_domain)

def initial_domain(pre_condition=[]):
    """
    domain is defined as an array of 3*7 elements, each of which is either 0 or 1 denoting off or on duty respectively.
    The total number of all possibilities for each employee is thus 2 to the 21st power. However, the majority of the
    possibilities are impratical. In practice, the most basic and the most important assumption is that one employee
    only works one shift a day.
    """
    one_day_shift = [ (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1) ]

    possible_shifts = set( [ shift_mon + shift_tue + shift_wed + shift_thu + shift_fri + shift_sat + shift_sun
                             for shift_mon in one_day_shift
                             for shift_tue in one_day_shift
                             for shift_wed in one_day_shift
                             for shift_thu in one_day_shift
                             for shift_fri in one_day_shift
                             for shift_sat in one_day_shift
                             for shift_sun in one_day_shift
    ] )

    print len(possible_shifts)

    for preprocess_func, args in pre_condition:
        if not args:
            possible_shifts = preprocess_func(possible_shifts)
        else:
            possible_shifts = preprocess_func(possible_shifts, *args)


    return possible_shifts


class GloabalConstraint(object):
    """
    A global constraint object which involves all the variables of the problem.
    """
    def __init__(self, var_names, check_func, description):
        self._var_names = var_names[:]
        self._check_func = check_func
        self._description = description

    def get_variable_names(self):
        return self._var_names

    def check(self, state, var_j_name=None, val_j=None):
        var_name_value_map = {}
        if var_j_name and val_j:
            var_name_value_map[var_j_name] = val_j

        for name in self._var_names:
            var = state.get_variable_by_name(name)
            value = var.get_assigned_value()
            if value:
                var_name_value_map[name] = value

        if var_name_value_map == {}:
            raise Exception("No value assigned!")

        return self._check_func(var_name_value_map)

    def __str__(self):
        return "Glabal constraint: %s" % self._description

class SS_CSPState(CSPState):
    def get_constraints_by_name(self, variable_name):
        constraints = []
        for key, val in self.constraint_map.items():
            if set(key).issuperset( set([variable_name]) ):
                constraints += val
        return constraints

class SS_CSP(CSP):
    def __init__(self, constraints, variables):
        self.constraint_map = {}
        for constraint in constraints:
            tup = constraint.get_variable_names()
            if tup not in self.constraint_map:
                lst = []
                self.constraint_map[tup] = lst
            else:
                lst = self.constraint_map[tup]
            lst.append(constraint)

        self.variable_map = {}
        self.variable_order = []
        for var in variables:
            self.variable_map[var.get_name()] = var
            self.variable_order.append(var.get_name())

    def initial_state(self):
        return SS_CSPState(self.constraint_map, self.variable_map,
                           self.variable_order, -1)

## Preprocess functions for the domain
def no_evening_shift_before_morning_shift(possible_shifts):
    to_be_removed = set([])
    for shift in possible_shifts:
        for i in xrange(0, 6):
            if shift[i*3 + 2] == 1 and shift[i*3 + 3] == 1:
                to_be_removed.add(shift)

    ps_set = possible_shifts.difference(to_be_removed)

    print "no_evening_shift_before_morning_shift: %s" % len(ps_set)
    return ps_set

def rest_days(possible_shifts):
    to_be_removed = set([])
    for shift in possible_shifts:
        rest_days = 0
        for i in xrange(0, 7):
            if not _is_on_duty(shift[i*3 : i*3+3]):
                rest_days += 1
        if rest_days == 0 or rest_days > 2:
            to_be_removed.add(shift)

    ps_set = possible_shifts.difference(to_be_removed)

    print "one_day_rest: %s" % len(ps_set)
    return ps_set

def at_most_three_days_work_in_a_row(possible_shifts):
    to_be_removed = set([])
    for shift in possible_shifts:
        consecutive_working_days = 0
        for i in xrange(0, 7):
            if _is_on_duty(shift[i*3 : i*3+3]):
                consecutive_working_days += 1
                if consecutive_working_days > 3:
                    to_be_removed.add(shift)
                    break
            else:
                consecutive_working_days = 0

    ps_set = possible_shifts.difference(to_be_removed)
    print "at_most_three_days_work_in_a_row: %s" % len(ps_set)
    return ps_set

def no_two_days_rest_in_a_row(possible_shifts):
    to_be_removed = set([])
    for shift in possible_shifts:
        consecutive_rest_days = 0
        for i in xrange(0, 7):
            if not _is_on_duty(shift[i*3 : i*3+3]):
                consecutive_rest_days += 1
                if consecutive_rest_days > 1:
                    to_be_removed.add(shift)
                    break
            else:
                consecutive_rest_days = 0

    ps_set = possible_shifts.difference(to_be_removed)
    print "no_two_days_rest_in_a_row: %s" % len(ps_set)
    return ps_set

def _is_on_duty(shifts_in_a_day):
    if reduce(lambda x, y: x+y, shifts_in_a_day) == 0:
        return False
    return True

no_checker = lambda state, verbose: True

def global_constraint_checker(state, verbose):
    if not state.get_current_variable_name():
        return True

    constraints = state.get_all_constraints()

    for constraint in constraints:
        if isinstance(constraint, GloabalConstraint):
            if not constraint.check(state):
                if verbose:
                    print "CONSTRAINT-FAILS: %s" %(constraint)
                return False
    return True

def global_forward_checking(state, verbose):
    basic = global_constraint_checker(state, verbose)
    if not basic:
        return False

    curr_var_name = state.get_current_variable_name()
    if not curr_var_name:
        # ROOT
        return True

    for constraint in state.get_all_constraints():
        all_var_names = constraint.get_variable_names()
        for var_j_name in  all_var_names:
            var_j = state.get_variable_by_name(var_j_name)
            for val in var_j.get_domain():
                if not constraint.check(state, var_j_name = var_j_name , val_j = val):
#                    print "Domain reduced!"
                    var_j.reduce_domain(val)

            if var_j.domain_size() ==  0:
                return False

    return True


def shift_schedule_problem():
    staff = [('John', 'Manager'),
 #            ('Joe', 'Manager'),
 #            ('Billy', 'Manager'),
 #            ('Bob', 'Manager'),
 #            ('Christina','Manager'),
             ('AA', 'Sales'),
 #            ('BB', 'Sales'),
 #            ('CC', 'Sales'),
 #            ('DD', 'Sales'),
 #            ('EE', 'Sales'),
 #            ('FF', 'Sales'),
 #            ('GG', 'Sales'),
 #            ('HH', 'Sales'),
 #            ('II', 'Sales'),
 #            ('JJ', 'Sales'),
 #            ('KK', 'Sales'),
 #            ('MM', 'Sales'),
 #            ('LL', 'Sales'),
 #            ('NN', 'Sales'),
 #            ('OO', 'Sales'),
    ]
    pre_condition = [(no_evening_shift_before_morning_shift, []),
                     (rest_days, []),
                     (at_most_three_days_work_in_a_row,[]),
                     (no_two_days_rest_in_a_row, [])]
    variables = []

    domain_statistics = [0]*21
    domain = list(initial_domain(pre_condition))
    for d in domain:
        for i in xrange(0, 21):
            if d[i] == 1:
                domain_statistics[i] += 1

    print domain_statistics

    for name, title in staff:
        ## Create employees
        variables.append( Employee(name, title, domain) )

    constraints = []
    def basic_assignment(var_name_map):
        values = var_name_map.values()
        assigned_shift_values = zip(*values)
        for shift_value in assigned_shift_values:
#            print "assigned shifted values: %s " % (shift_value,)
            if shift_weighted_sum(shift_value) > 200:
                return False
            elif len(values) == len(staff) and shift_weighted_sum(shift_value) < 101:
                return False
            else:
                pass
        return True

    constraints.append(GloabalConstraint(tuple([variable.get_name() for variable in variables]),
                                         basic_assignment,
                                         "Basic assignment contains at least 1 manager") )
    return SS_CSP(constraints, variables)

def shift_weighted_sum(shift_value):
    return reduce(lambda x,y: x+y, shift_value)

if __name__ == '__main__':
    checker = global_forward_checking
    solve_csp_problem(shift_schedule_problem, checker, verbose=False)
