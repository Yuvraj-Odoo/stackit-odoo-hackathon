from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Vote(models.Model):
    _name = 'stackit.vote'
    _description = 'Vote'
    _rec_name = 'vote_type'

    vote_type = fields.Selection([
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote')],
        string='Vote Type',
        required=True
    )
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)
    question_id = fields.Many2one('stackit.question', string='Question', ondelete='cascade')
    answer_id = fields.Many2one('stackit.answer', string='Answer', ondelete='cascade')
    create_date = fields.Datetime(string='Voted On', default=fields.Datetime.now)

    _sql_constraints = [
        ('user_question_unique', 'unique(user_id, question_id)', 'You can only vote once per question!'),
        ('user_answer_unique', 'unique(user_id, answer_id)', 'You can only vote once per answer!'),
    ]

    @api.constrains('question_id', 'answer_id')
    def _check_vote_target(self):
        for vote in self:
            if not vote.question_id and not vote.answer_id:
                raise ValidationError(_("Vote must be for either a question or answer."))
            if vote.question_id and vote.answer_id:
                raise ValidationError(_("Vote cannot be for both question and answer."))

    @api.model
    def create(self, vals):
        if 'user_id' not in vals:
            vals['user_id'] = self.env.user.id
        
        # Check if user is voting on their own content
        if vals.get('question_id'):
            question = self.env['stackit.question'].browse(vals['question_id'])
            if question.user_id.id == vals['user_id']:
                raise ValidationError(_("You cannot vote on your own question."))
        
        if vals.get('answer_id'):
            answer = self.env['stackit.answer'].browse(vals['answer_id'])
            if answer.user_id.id == vals['user_id']:
                raise ValidationError(_("You cannot vote on your own answer."))
        
        return super(Vote, self).create(vals)