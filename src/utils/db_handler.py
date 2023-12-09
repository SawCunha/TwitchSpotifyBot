from utils.errors import *
from utils.logger import Log
from os.path import exists
import sqlite3
import time


class DB:
    def __init__(self, log: Log, db_path: str = './data/app.sqlite'):
        
        if not exists(db_path):
            with open(db_path, 'w') as f:
                f.close()
        
        self.db = sqlite3.connect(db_path)
        self.cursor = self.db.cursor()
        self.log = log
        self.user_tb = 'users'
        self.leaderboard_reset = 'lb_reset'
        self.cursor.execute(
            f'CREATE TABLE IF NOT EXISTS {self.user_tb} (username VARCHAR(50) NOT NULL, ban TINYINT, moderator TINYINT, administrator TINYINT, \
            requests SMALLINT, rates SMALLINT, rates_given SMALLINT, PRIMARY KEY (username))')
        self.cursor.execute(
            f'CREATE TABLE IF NOT EXISTS {self.leaderboard_reset} (win_id INTEGER PRIMARY KEY AUTOINCREMENT, winner VARCHAR(50), date INT, next_reset_date INT, sp_mod_given TINYINT, \
            win_active TINYINT DEFAULT 1)')

    def error_handler(self, error, func):
        self.log.error(f'Error in {func.__name__}: {error}')
        raise DBError

    def check(func: callable):
        def wrapper(self, *args, **kwargs):

            args = list(args)
            for ind, item in enumerate(args):
                if isinstance(item, str):
                    item = item.replace("'", "''")
                    item = item.replace('"', '""')
                    item = item.replace('&', '')
                    item = item.replace('--', '')
                    args[ind] = item
            
            for kwarg in kwargs.keys():
                item = kwargs[kwarg]
                if isinstance(item, str):
                    item = item.replace("'", "''")
                    item = item.replace('"', '""')
                    item = item.replace('&', '')
                    item = item.replace('--', '')
                    kwargs[kwarg] = item
                
            try:
                return func(self, *args, **kwargs)
            except Exception as er:
                self.error_handler(er, func)
                return None
            
        return wrapper

    @check
    def remove_active_lb(self, win_id: int):
        sql = f"UPDATE {self.leaderboard_reset} SET win_active = 0 WHERE win_id = {win_id}"
        self.cursor.execute(sql)
        self.db.commit()
    
    @check
    def get_last_reset(self):
        sql = f"SELECT * FROM {self.leaderboard_reset} WHERE win_active = 1"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if results is None:
            return None
        if len(results) == 0:
            return None
        else:
            return results[-1]

    @check
    def reset_leaderboard(self, winner: str, period: str, rewards: dict):
        date = int(time.time())
        if period == 'weekly':
            next_reset_date = date + 604800
        elif period == 'monthly':
            next_reset_date = date + 2592000
        self.add_leaderboard_winner(winner, date, next_reset_date, bool(rewards['sp_mod']))
        self.reset_all_user_stats()

    @check
    def get_all_resets(self):
        sql = f"SELECT * FROM {self.leaderboard_reset}"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    @check
    def add_leaderboard_winner(self, winner: str, start_date, end_date, sp_mod_given: bool):
        sql = f"INSERT INTO {self.leaderboard_reset} (winner, date, next_reset_date, sp_mod_given) VALUES ('{winner}', {start_date}, {end_date}, {int(sp_mod_given)})"
        self.cursor.execute(sql)
        self.db.commit()
        self.get_all_resets()

    @check
    def get_leader(self):
        sql = f"SELECT username, rates FROM {self.user_tb} WHERE rates > 0 ORDER BY rates DESC"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if results is None:
            return None
        if len(results) == 0:
            return None
        else:
            return results[0]

    @check
    def check_user_exists(self, username):
        sql = f"SELECT * FROM {self.user_tb} WHERE username = '{username}'"
        self.cursor.execute(sql)
        if len(self.cursor.fetchall()) == 0:
            self.init_user(username)
            return False
        else:
            return True

    @check
    def init_user(self, username: str, ban=0, mod=0, admin=0, requests=0, rates=0, rates_given=0):
        sql = f"INSERT INTO {self.user_tb} VALUES ('{username}', {ban}, {mod}, {admin}, {requests}, {rates}, {rates_given})"
        self.cursor.execute(sql)
        self.db.commit()
        self.log.info(f'Initialized {username}')
        return True

    @check
    def delete_user(self, username: str):
        sql = f"DELETE FROM {self.user_tb} WHERE username = '{username}'"
        self.cursor.execute(sql)
        self.db.commit()
        if self.cursor.rowcount > 0:
            self.log.info(f'Deleted user: {username}')
            return True
        else:
            return False

    @check
    def update_user(self, username: str, update: dict):
        for col in update.keys():
            sql = f"UPDATE {self.user_tb} SET {col} = '{update[col]}' WHERE username = '{username}'"
            self.cursor.execute(sql)
            self.db.commit()

    @check
    def get_all_users(self):
        sql = f"SELECT username FROM {self.user_tb}"
        self.cursor.execute(sql)
        return [user[0] for user in self.cursor.fetchall()]

    @check
    def get_user_full(self, username: str):
        sql = f"SELECT * FROM {self.user_tb} WHERE username = '{username}'"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()[0]
        return {'ban': bool(results[1]), 'mod': bool(results[2]), 'admin': bool(results[3]),
                'requests': int(results[4]), 'rates': int(results[5]), 'rates given': int(results[6])}

    @check
    def is_user_banned(self, username: str):
        sql = f"SELECT ban FROM {self.user_tb} WHERE username = '{username}'"
        self.cursor.execute(sql)
        return bool(self.cursor.fetchall()[0][0])

    @check
    def is_user_mod(self, username: str):
        sql = f"SELECT moderator FROM {self.user_tb} WHERE username = '{username}'"
        self.cursor.execute(sql)
        return bool(self.cursor.fetchall()[0][0])

    @check
    def is_user_admin(self, username: str):

        sql = f"SELECT administrator FROM {self.user_tb} WHERE username = '{username}'"
        self.cursor.execute(sql)
        return bool(self.cursor.fetchall()[0][0])

    @check
    def is_user_privileged(self, username: str):

        sql = f"SELECT moderator, administrator FROM {self.user_tb} WHERE username = '{username}'"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        for res in results:
            if bool(res[0]) is True:
                return True
        return False

    @check
    def remove_privilege_user(self, username: str):

        sql = f"UPDATE {self.user_tb} SET administrator = '0', moderator = '0' WHERE username = '{username}'"
        self.cursor.execute(sql)
        self.db.commit()

    @check
    def ban_user(self, username: str):

        self.remove_privilege_user(username)
        sql = f"UPDATE {self.user_tb} SET ban = '1' WHERE username = '{username}'"
        self.cursor.execute(sql)
        self.db.commit()
        self.log.info(f'Banned user: {username}')


    @check
    def unban_user(self, username: str):

        sql = f"UPDATE {self.user_tb} SET ban = '0' WHERE username = '{username}'"
        self.cursor.execute(sql)
        self.db.commit()
        self.log.info(f'Unbanned user: {username}')

    @check
    def mod_user(self, username: str):

        self.unban_user(username)
        sql = f"UPDATE {self.user_tb} SET moderator = '1' WHERE username = '{username}'"
        self.cursor.execute(sql)
        self.db.commit()

    @check
    def admin_user(self, username: str):

        self.mod_user(username)
        sql = f"UPDATE {self.user_tb} SET administrator = '1' WHERE username = '{username}'"
        self.cursor.execute(sql)
        self.db.commit()

    @check
    def add_rate(self, receiver, giver):

        sql = f"UPDATE {self.user_tb} SET rates = rates + 1 WHERE username = '{receiver}'"
        self.cursor.execute(sql)
        sql2 = f"UPDATE {self.user_tb} SET rates_given = rates_given + 1 WHERE username = '{giver}'"
        self.cursor.execute(sql2)
        self.db.commit()

    @check
    def add_requests(self, username: str):

        sql = f"UPDATE {self.user_tb} SET requests = requests + 1 WHERE username = '{username}'"
        self.cursor.execute(sql)
        self.db.commit()

    @check
    def reset_all_user_stats(self):

        sql = f"UPDATE {self.user_tb} SET requests = '0', rates = '0', rates_given = '0'"
        self.cursor.execute(sql)
        self.db.commit()
        self.log.info('All user stats have been reset')

    @check
    def get_user_stats(self, username: str):

        sql = f"SELECT rates, requests, rates_given FROM {self.user_tb} WHERE username = '{username}'"
        self.cursor.execute(sql)
        info = self.cursor.fetchall()
        if len(info) == 0:
            return None
        info = info[0]

        sql2 = f"SELECT username FROM {self.user_tb} ORDER BY rates DESC"
        self.cursor.execute(sql2)
        sorted_users = [user[0] for user in self.cursor.fetchall()]
        pos = sorted_users.index(username) + 1

        return {'pos': pos, 'requests': info[1], 'rates': info[0], 'rates given': info[2]}

    @check
    def get_leaderboard(self):

        sql = f"SELECT username, rates FROM {self.user_tb} WHERE rates > 0 ORDER BY rates DESC"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return self.format_user_results(results)

    @check
    def format_user_results(self, results, limit=50):
        sorted_users = []
        sorted_rates = []
        sorted_position = []
        i = 1
        for res in results[:limit]:
            sorted_position.append(str(i))
            sorted_users.append(str(res[0]))
            sorted_rates.append(str(res[1]))
            i += 1
        sorted_position = ' \n '.join(sorted_position)
        sorted_users = ' \n '.join(sorted_users)
        sorted_rates = ' \n '.join(sorted_rates)
        if len(sorted_users) > 1024:
            return self.format_user_results(results, limit=limit - 5)
        else:
            return sorted_position, sorted_users, sorted_rates

    @check
    def delete_all(self):
        self.cursor.execute(f"DELETE FROM {self.user_tb}")
        self.cursor.execute(f"DELETE FROM {self.leaderboard_reset}")
        self.db.commit()
