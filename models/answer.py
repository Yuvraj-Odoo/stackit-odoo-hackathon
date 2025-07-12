from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class Answer(models.Model):
    _name = 'stackit.answer'
    _description = 'Answer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'vote_count desc, create_date desc'

    content = fields.Html(string='Answer', sanitize=False, required=True)
    plain_content = fields.Text(string='Plain Text', compute='_compute_plain_content', store=True)
    question_id = fields.Many2one('stackit.question', string='Question', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Author', default=lambda self: self.env.user)
    vote_ids = fields.One2many('stackit.vote', 'answer_id', string='Votes')
    vote_count = fields.Integer(string='Vote Count', compute='_compute_vote_count', store=True)
    is_accepted = fields.Boolean(string='Accepted Answer', default=False)
    create_date = fields.Datetime(string='Posted On', default=fields.Datetime.now)
    last_edit_date = fields.Datetime(string='Last Edited', readonly=True)
    edit_count = fields.Integer(string='Edit Count', default=0)
    active = fields.Boolean(string='Active', default=True)

    @api.depends('content')
    def _compute_plain_content(self):
        for answer in self:
            answer.plain_content = tools.html2plaintext(answer.content or '')

    @api.depends('vote_ids.vote_type')
    def _compute_vote_count(self):
        for answer in self:
            answer.vote_count = sum(
                1 for vote in answer.vote_ids if vote.vote_type == 'upvote'
            ) - sum(
                1 for vote in answer.vote_ids if vote.vote_type == 'downvote'
            )

    def action_accept_answer(self):
        self.ensure_one()
        if self.env.user != self.question_id.user_id:
            raise UserError(_("Only the question author can accept answers."))
        self.question_id.answer_ids.write({'is_accepted': False})
        self.write({'is_accepted': True})

    def action_edit(self, content):
        self.ensure_one()
        if self.env.user != self.user_id:
            raise UserError(_("Only the answer author can edit."))
        self.write({
            'content': content,
            'last_edit_date': fields.Datetime.now(),
            'edit_count': self.edit_count + 1
        })

    @api.model
    def create(self, vals):
        answer = super(Answer, self).create(vals)
        answer.question_id._notify_answer_posted(answer)
        return answer

    def unlink(self):
        for answer in self:
            if answer.is_accepted:
                raise UserError(_("Cannot delete an accepted answer."))
        return super(Answer, self).unlink()