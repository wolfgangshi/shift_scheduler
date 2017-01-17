#from classify import *
import math

##
## CSP portion of lab 4.
##
from csp import BinaryConstraint, CSP, CSPState, Variable,\
    basic_constraint_checker, solve_csp_problem

# Implement basic forward checking on the CSPState see csp.py
def forward_checking(state, verbose=False):
    # Before running Forward checking we must ensure
    # that constraints are okay for this state.
    basic = basic_constraint_checker(state, verbose)
    if not basic:
        return False

    # Add your forward checking logic here.
    # 1. Find X = x being the current assignment.
    # 2. for each Y that is associated with X in a binary constraint; do
    #        for each y in Y's Domain; do
    #            if X=x and Y=y don't hold:
    #                 remove y from Y's Domain
    #                 if Y's Domain is empty:
    #                    return False
    #    return True

    # NOTE: This function is not a pure function. Its side-effect is
    #       to update the state
    curr_var_name = state.get_current_variable_name()
    if not curr_var_name:
        # ROOT
        return True

    for constraint in state.get_constraints_by_name(curr_var_name):
        var_j = state.get_variable_by_name( constraint.get_variable_j_name() )
        for val in var_j.get_domain():
            if not constraint.check(state, value_i = None, value_j = val):
                var_j.reduce_domain(val)

            if var_j.domain_size() ==  0:
                return False

    return True

# Now Implement forward checking + (constraint) propagation through
# singleton domains.
def forward_checking_prop_singleton(state, verbose=False):
    # Run forward checking first.
    fc_checker = forward_checking(state, verbose)
    if not fc_checker:
        return False

    # Add your propagate singleton logic here.
    singleton_queue = [ var for var in state.get_all_variables() if var.domain_size() == 1 ]
    visited_singletons = set([])

    while singleton_queue:
        var = singleton_queue.pop(0)

        visited_singletons.add(var)
        for constraint in state.get_constraints_by_name(var.get_name()):
            var_j = state.get_variable_by_name( constraint.get_variable_j_name() )
            for val_j in var_j.get_domain():
                if not constraint.check(state, var.get_domain()[0], val_j):
                    var_j.reduce_domain(val_j)

                if var_j.domain_size() == 0:
                    return False

            if var_j.domain_size() == 1 and not visited_singletons.issuperset(set([var_j])):
                singleton_queue.append(var_j)

    return True

## The code here are for the tester
## Do not change.
