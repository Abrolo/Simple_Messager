class EmailService:
    def __init__(self, db):
        self.db = db
        
    def get_limit_and_offset(self, start_index=0, stop_index=0):
        if type(start_index) == int and type(stop_index) == int:
            if stop_index > start_index:
                return stop_index - start_index, start_index
    def get_emails(self, start=None, stop=None):
        if start is not None and stop is not None:
            limit, offset = self.get_limit_and_offset(start, stop)
            emails = self.fetch_paginated_emails(limit, offset)
        else:
            emails = self.fetch_all_emails()
        return [dict(email) for email in emails]
    
    def fetch_all_emails(self):
        query = """
            SELECT * FROM email
            ORDER BY created_at DESC
        """
        return self.db.execute(query).fetchall()

    def fetch_paginated_emails(self, limit, offset):
        query = '''
            SELECT *
            FROM email e
            ORDER BY e.created_at DESC
            LIMIT ? OFFSET ?
        '''
        return self.db.execute(query, (limit, offset)).fetchall()