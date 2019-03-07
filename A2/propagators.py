'''
This file will contain different constraint propagators to be used within 
bt_search.

---
A propagator is a function with the following header
    propagator(csp, newly_instantiated_variable=None)

csp is a CSP object---the propagator can use this to get access to the variables 
and constraints of the problem. The assigned variables can be accessed via 
methods, the values assigned can also be accessed.

newly_instantiated_variable is an optional argument. SEE ``PROCESSING REQUIRED''
if newly_instantiated_variable is not None:
    then newly_instantiated_variable is the most
    recently assigned variable of the search.
else:
    propagator is called before any assignments are made
    in which case it must decide what processing to do
    prior to any variables being assigned. 

The propagator returns True/False and a list of (Variable, Value) pairs, like so
    (True/False, [(Variable, Value), (Variable, Value) ...]

Propagators will return False if they detect a dead-end. In this case, bt_search 
will backtrack. Propagators will return true if we can continue.

The list of variable value pairs are all of the values that the propagator 
pruned (using the variable's prune_value method). bt_search NEEDS to know this 
in order to correctly restore these values when it undoes a variable assignment.

Propagators SHOULD NOT prune a value that has already been pruned! Nor should 
they prune a value twice.

---

PROCESSING REQUIRED:
When a propagator is called with newly_instantiated_variable = None:

1. For plain backtracking (where we only check fully instantiated constraints)
we do nothing...return true, []

2. For FC (where we only check constraints with one remaining 
variable) we look for unary constraints of the csp (constraints whose scope 
contains only one variable) and we forward_check these constraints.

3. For GAC we initialize the GAC queue with all constaints of the csp.

When a propagator is called with newly_instantiated_variable = a variable V

1. For plain backtracking we check all constraints with V (see csp method
get_cons_with_var) that are fully assigned.

2. Fonr forward checkig we forward check all constraints with V that have one
unassigned variable left

3. For GAC we initialize the GAC queue with all constraints containing V.

'''


def prop_BT(csp, newVar=None):
    '''
    Do plain backtracking propagation. That is, do no propagation at all. Just 
    check fully instantiated constraints.
    '''
    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []


def prop_FC(csp, newVar=None):
    # newVar == None.
    if not newVar:
        cons = csp.get_all_cons()

    # newVar != None.
    else:
        cons = csp.get_cons_with_var(newVar)

    # Get all unary constraints in cons.
    unary_cons = [con for con in cons if con.get_n_unasgn() == 1]

    # Pruned values will be saved in this list, and return at end.
    pruned_vars = []

    # Forward Checking Algorithm in the lecture note (p51).
    for con in unary_cons:

        # Con must have only one unassigned variable in its scope.
        unasgn_var = con.get_unasgn_vars()[0]
        vals_left = unasgn_var.cur_domain()

        # FCCheck in the lecture note (p50).
        for val in vals_left:

            # Assign a (potentially wrong) value for now.
            unasgn_var.assign(val)
            # Now all var in con has an assigned value, so we can use function check(vals).
            vals = [var.get_assigned_value() for var in con.get_scope()]

            # Remove this value, if it is unsatisfied.
            if not con.check(vals):
                # Propagators should not prune a value that has already been pruned; nor should they prune a value
                # twice. It is be safer to have this if-condition check.
                if unasgn_var.in_cur_domain(val):
                    unasgn_var.prune_value(val)
                    pruned_vars.append((unasgn_var, val))

            # Change the var back.
            unasgn_var.unassign()

        # DWO. This DWO-check didn't work correctly when it was in the for-loop above.
        if unasgn_var.cur_domain_size() == 0:
            return False, pruned_vars

    # No dead-end.
    return True, pruned_vars


def prop_GAC(csp, newVar=None):
    '''
    Do GAC propagation. If newVar is None we do initial GAC enforce processing 
    all constraints. Otherwise we do GAC enforce with constraints containing 
    newVar on GAC Queue.
    '''

    # newVar == None.
    if not newVar:
        # Use List as a Queue.
        cons = csp.get_all_cons()

    # newVar != None.
    else:
        cons = csp.get_cons_with_var(newVar)

    # Pruned values will be saved in this list, and return at end.
    pruned_vars = []

    # GAC_Enforce in the lecture note (p89).
    while len(cons) != 0:

        con = cons.pop(0)

        # Variables in this constraint.
        for var in con.get_scope():

            # Remaining values in var's domain.
            for val in var.cur_domain():

                # Con(A + val) is not ture,
                # i.e. there does not exist any assignment A for other variables such that A with val satisfies Con.
                if not con.has_support(var, val):

                    # Remove this unsatisfied value.
                    if var.in_cur_domain(val):
                        var.prune_value(val)
                        pruned_vars.append((var, val))

                    # DWO.
                    if var.cur_domain_size() == 0:
                        return False, pruned_vars

                    # Push each con containing var on/back to the Queue.
                    else:
                        # Don't add con again, if it is already on the Queue.
                        # Maybe I should use set.
                        cons.extend([more_con for more_con in csp.get_cons_with_var(var) if not more_con in cons])

    # No dead-end.
    return True, pruned_vars
