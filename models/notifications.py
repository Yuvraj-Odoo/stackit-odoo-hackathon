from odoo import models, fields, api, _
from odoo.tools import html2plaintext

class Notification(models.Model):
    _name = 'stackit.notification'
    _description = 'User Notification'
    _order = 'create_date desc'

    user_id = fields.Many2one('res.users', string='User', required=True, index=True)
    message = fields.Text(string='Message', required=True)
    notification_type = fields.Selection([
        ('answer', 'New Answer'),
        ('comment', 'Comment'),
        ('mention', 'Mention'),
        ('vote', 'Vote'),
        ('system', 'System')
    ], string='Type', required=True)
    is_read = fields.Boolean(string='Read', default=False)
    related_question_id = fields.Many2one('stackit.question', string='Related Question')
    related_answer_id = fields.Many2one('stackit.answer', string='Related Answer')
    create_date = fields.Datetime(string='Date', default=fields.Datetime.now)

    def mark_as_read(self):
        self.write({'is_read': True})

    @api.model
    def create_notification(self, user_id, message, notif_type, question_id=None, answer_id=None):
        """ Centralized notification creation """
        return self.create({
            'user_id': user_id,
            'message': html2plaintext(message)[:500],  # Truncate long messages
            'notification_type': notif_type,
            'related_question_id': question_id,
            'related_answer_id': answer_id
        })

    def action_view_related(self):
        self.ensure_one()
        if self.related_question_id:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/question/{self.related_question_id.id}',
                'target': 'self'
            }
        return False

    def _gc_old_notifications(self, days=30):
        """ Garbage collect old notifications """
        deadline = fields.Datetime.subtract(fields.Datetime.now(), days=days)
        return self.search([('create_date', '<', deadline)]).unlink()