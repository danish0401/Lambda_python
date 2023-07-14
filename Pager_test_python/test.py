def get_pagerduty_users_slack_ids(users):
    
    slack_mapping = {}
    slack_mapping  ={
        'Wajahat Chaudhry' : 'UFN7Q9S04',
        'Junaid Malik' : 'U039016GG0K',
        'Danish Hafeez' : 'U03LJ0KDM5W',
        'Akbar Alam' : 'U03QTU888CQ',
        'Faisal Nawaz' : 'U0413TQ3G1G'
    }

    slack_ids = []

    for user in users:
        slack_ids.append(slack_mapping[user])

    return slack_ids

def get_pagerduty_oncall_users():
    return ['Danish Hafeez', 'Faisal Nawaz']


users= get_pagerduty_oncall_users()
ids=get_pagerduty_users_slack_ids(users)

print(ids)