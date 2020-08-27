import sys
sys.path.append('./')
from DataConnecter import Database

d = Database()
#
# query = '''Create TABLE IF NOT EXISTS `behavior pattern` (
# 	`uid` VARCHAR(2),
#     `place_id` VARCHAR(100),
#     `happened_times` INT,
#     `last_time` DATETIME,
# '''
# for hour in range(24):
# 	query+="    {}_{}_freq INT NOT NULL DEFAULT 0,\n".format(hour,hour+1)
#
# query+='''PRIMARY KEY(`uid`,`place_id`),
# FOREIGN KEY(`uid`) REFERENCES User(`uid`) ON DELETE CASCADE
# );
# '''
# print(query)
# d.cursor.execute(query)
# d.db.commit()

query = '''INSERT IGNORE INTO `behavior pattern`(uid,event)
VALUES("1","{}")'''
for event in ['gym','meal','work','home','school','coffee','grocery']:
	d.cursor.execute(query.format(event))
	d.db.commit()
