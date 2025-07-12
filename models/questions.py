# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class Question(models.Model):
    _name = 'stackit.question'
    _description = 'Question'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.seo.metadata', 'website.published.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Title', required=True, translate=True, tracking=True)
    description = fields.Html(string='Description', sanitize=False, strip_style=True, tracking=True)
    content = fields.Text(string='Plain Content', compute='_compute_plain_content', store=True)
    user_id = fields.Many2one('res.users', string='Author', default=lambda self: self.env.user, required=True)
    tag_ids = fields.Many2many('stackit.tag', string='Tags', domain="[('active', '=', True)]")
    answer_ids = fields.One2many('stackit.answer', 'question_id', string='Answers')
    favorite_ids = fields.Many2many('res.users', string='Favorited By')
    vote_ids = fields.One2many('stackit.vote', 'question_id', string='Votes')
    vote_count = fields.Integer(string='Vote Count', compute='_compute_vote_count', store=True)
    answer_count = fields.Integer(string='Answer Count', compute='_compute_answer_count', store=True)
    view_count = fields.Integer(string='View Count', default=0)
    closed = fields.Boolean(string='Closed', default=False)
    closed_reason = fields.Text(string='Close Reason')
    closed_by = fields.Many2one('res.users', string='Closed By')
    closed_date = fields.Datetime(string='Closed Date')
    last_activity_date = fields.Datetime(string='Last Activity', compute='_compute_last_activity', store=True)
    active = fields.Boolean(string='Active', default=True)
    website_id = fields.Many2one('website', string='Website', default=lambda self: self.env['website'].get_current_website())
    can_edit = fields.Boolean(string='Can Edit', compute='_compute_can_edit')

    @api.depends('description')
    def _compute_plain_content(self):
        for question in self:
            question.content = tools.html2plaintext(question.description or '')

    @api.depends('vote_ids.vote_type')
    def _compute_vote_count(self):
        for question in self:
            question.vote_count = sum(
                1 for vote in question.vote_ids if vote.vote_type == 'upvote'
            ) - sum(
                1 for vote in question.vote_ids if vote.vote_type == 'downvote'
            )

    @api.depends('answer_ids')
    def _compute_answer_count(self):
        for question in self:
            question.answer_count = len(question.answer_ids)

    @api.depends('write_date', 'answer_ids.write_date')
    def _compute_last_activity(self):
        for question in self:
            dates = [question.write_date]
            dates.extend(answer.write_date for answer in question.answer_ids)
            question.last_activity_date = max(dates)

    def _compute_can_edit(self):
        for question in self:
            question.can_edit = (
                self.env.user == question.user_id or 
                self.env.user.has_group('stackit_odoo_hackathon.group_question_moderator')
            )

    def increment_view_count(self):
        self.ensure_one()
        self.sudo().write({'view_count': self.view_count + 1})

    def action_close_question(self, reason=None):
        self.ensure_one()
        if not self.env.user.has_group('stackit_odoo_hackathon.group_question_moderator'):
            raise UserError(_("Only moderators can close questions."))
        self.write({
            'closed': True,
            'closed_reason': reason,
            'closed_by': self.env.user.id,
            'closed_date': fields.Datetime.now()
        })
        return True

    def action_reopen_question(self):
        self.ensure_one()
        if not self.env.user.has_group('stackit_odoo_hackathon.group_question_moderator'):
            raise UserError(_("Only moderators can reopen questions."))
        self.write({
            'closed': False,
            'closed_reason': None,
            'closed_by': None,
            'closed_date': None
        })
        return True

    def _get_share_url(self, redirect=False, share_type=None, **kwargs):
        self.ensure_one()
        return '/question/%s' % self.id

    @api.model
    def create(self, vals):
        if 'name' in vals and not vals.get('description'):
            raise ValidationError(_("Please provide a detailed description of your question."))
        return super(Question, self).create(vals)

    def write(self, vals):
        if 'name' in vals and not vals.get('description'):
            raise ValidationError(_("Please provide a detailed description when editing your question."))
        return super(Question, self).write(vals)

    def unlink(self):
        for question in self:
            if question.answer_count > 0:
                raise UserError(_("You cannot delete a question that has answers."))
        return super(Question, self).unlink()

    def get_related_questions(self, limit=5):
        self.ensure_one()
        return self.search([
            ('tag_ids', 'in', self.tag_ids.ids),
            ('id', '!=', self.id),
            ('active', '=', True)
        ], limit=limit)

    def _notify_answer_posted(self, answer):
        self.ensure_one()
        self.message_post(
            body=_("New answer posted by %s") % answer.user_id.name,
            subject=_("New Answer"),
            partner_ids=[self.user_id.partner_id.id],
            message_type='comment',
            subtype_xmlid='mail.mt_comment'
        )