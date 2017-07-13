import re

input_file = open("TMSInput.txt", 'rU').read().split('\n')

status = []
TMS = {}
rules = {}
stack = []


def add_rule(stack, orig_rule, pat):
    rule = ""
    while stack:
        item = stack.pop()
        if item == '+':
            if rules.get(rule):
                rules[rule].append([pat, orig_rule, False])
            else:
                rules[rule] = [[pat, orig_rule, False]]
            rule = ""
        else:
            if item == '*':
                item = ','
            rule = item + rule
    if rules.get(rule):
        rules[rule].append([pat, orig_rule, False])
    else:
        rules[rule] = [[pat, orig_rule, False]]


def assess_rules():
    if not rules:
        return
    rules_copy = rules.copy()
    for key in rules_copy.keys():
        found = True
        for k in key.split(','):
            if not TMS.get(k):
                found = False
        if found:
            r_list = rules[key].copy()
            for rule_list in r_list:
                if not rule_list[2]:
                    rule_list[2] = True
                    str = '{' + key + ',' + rule_list[1] + '}'
                    if TMS.get(rule_list[0]):
                        TMS[rule_list[0]].append(str)
                    else:
                        TMS[rule_list[0]] = [str]
                    status.append(rule_list[0]+':'+str)
    if rules_copy != rules:
        assess_rules()


def delete_literals(literal):
    deleted = []
    for key in rules.keys():
        for k in key.split(','):
            if k == literal:
                r_list = rules[key].copy()
                for rule_list in r_list:
                    if rule_list[2]:
                        rule_list[2] = False
                        str = '{' + key + ',' + rule_list[1] + '}'
                        if TMS.get(rule_list[0]):
                            TMS[rule_list[0]].remove(str)
                            deleted.append(rule_list[0])
                            if not TMS[rule_list[0]]:
                                TMS.pop(rule_list[0])
                        status.remove(rule_list[0] + ':' + str)
    while deleted:
        delete_literals(deleted.pop(0))


def delete_rules(rule, literal):
    status.remove(rule)

    rules_copy = rules.copy()
    for r in rules_copy:
        l_copy = rules[r].copy()
        for l in l_copy:
            if l[1] == rule:
                rules[r].remove(l)
    rules_copy = rules.copy()
    for r in rules_copy:
        if not rules_copy[r]:
            rules.pop(r)

    def delete_recursive(r,literal):
        to_delete = literal
        delete_rule = ',' + r + '}'
        status_copy = status.copy()
        for i in status_copy:
            if delete_rule in i:
                status.remove(i)
        TMS_list = TMS[to_delete].copy()
        for i in TMS_list:
            if delete_rule in i:
                TMS[to_delete].remove(i)
        if not TMS[to_delete]:
            TMS.pop(to_delete)
            if rules.get(to_delete):
                for i in rules[to_delete]:
                    if i[2]:
                        i[2] = False
                        delete_recursive(i[1],i[0])

    delete_recursive(rule,literal)


for line in input_file:

    if line.startswith('T'):

        # Rule
        pattern = re.search(r'Tell:(([\w+*-]*\w)->(-*\w))', line)
        if pattern:
            status.append(pattern.group(1))
            for i in pattern.group(2):
                stack.append(i)
            add_rule(stack, pattern.group(1), pattern.group(3))
            assess_rules()
            assess_rules()
            continue

        # Single positive literal
        pattern = re.search(r'Tell:(-*\w)', line)
        if pattern:
            str = pattern.group(1)
            if TMS.get(str):
                flag = False
                for i in TMS.get(str):
                    if i == str:
                        flag = True
                        break
                if flag == True:
                    continue
                status.append(str)
                TMS[str].append(str)
                assess_rules()
                assess_rules()
                continue
            status.append(str)
            TMS[str] = [str]
            assess_rules()
            assess_rules()
            continue

    elif line.startswith('R'):
        # Rule
        pattern = re.search(r'Retract:(([\w+*-]*\w)->(-*\w))', line)
        if pattern:
            if pattern.group(1) in status:
                delete_rules(pattern.group(1),pattern.group(3))
            continue

        pattern = re.search(r'Retract:(-*\w)', line)
        if pattern:
            str = pattern.group(1)
            if str in status:
                if TMS.get(str):
                    for i in TMS.get(str):
                        if i == str:
                            TMS[str].remove(i)
                            break
                    delete_literals(str)
                    status.remove(str)
                    if not TMS[str]:
                        TMS.pop(str)
                    continue
            continue

print("Final Status of TMS:")
for each in status:
    print(each)