import sys
sys.path.append('./')
from DataConnecter import Database
from pathlib import Path

d = Database()

query = '''Create TABLE IF NOT EXISTS `location frequency` (
	`uid` VARCHAR(2),
    `place_id` VARCHAR(100),
'''

for hour in range(24):
	query+="    {}_{}_freq INT NOT NULL DEFAULT 0,\n".format(hour,hour+1)

	query+="	{}_{}_recent_time datetime,\n".format(hour,hour+1)

query+='''PRIMARY KEY(`uid`,`place_id`),
FOREIGN KEY(`uid`) REFERENCES User(`uid`) ON DELETE CASCADE
);
'''
print(query)
d.cursor.execute(query)
d.db.commit()

# for uid in range(1,6):
#     add_query="INSERT IGNORE INTO user(uid) VALUES({})"
#     d.cursor.execute(add_query.format(uid))
#     d.db.commit()

# add_query = "INSERT INTO user VALUES(%s)"
# val = ("6",)
# d.cursor.execute(add_query,val)
# d.db.commit()
# path = Path.cwd()/'data builder'/'sql'/'Address Type.txt'
# with open(path,"r") as fp:
# 	for line in fp:
# 		query = '''INSERT INTO `address type`(type)
# 		VALUE("{}")'''.format(line.strip())
# 		d.cursor.execute(query)
# 		d.db.commit()
