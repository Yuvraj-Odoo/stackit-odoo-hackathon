from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Tag(models.Model):
    _name = 'stackit.tag'
    _description = 'Question Tag'
    _order = 'question_count desc, name asc'

    name = fields.Char(string='Tag Name', required=True, translate=True)
    description = fields.Text(string='Description')
    color = fields.Integer(string='Color Index')
    question_count = fields.Integer(string='Question Count', compute='_compute_question_count', store=True)
    active = fields.Boolean(string='Active', default=True)
    moderator_only = fields.Boolean(string='Moderator Only')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]

    @api.depends('question_ids')
    def _compute_question_count(self):
        for tag in self:
            tag.question_count = len(tag.question_ids)

    @api.model
    def create(self, vals):
        if 'moderator_only' in vals and vals['moderator_only'] and not self.env.user.has_group('stackit_odoo_hackathon.group_moderator'):
            raise ValidationError(_("Only moderators can create restricted tags."))
        return super(Tag, self).create(vals)

    def write(self, vals):
        if 'moderator_only' in vals and vals['moderator_only']:
            if not self.env.user.has_group('stackit_odoo_hackathon.group_moderator'):
                raise ValidationError(_("Only moderators can modify restricted tags."))
        return super(Tag, self).write(vals)

    def name_get(self):
        result = []
        for tag in self:
            name = tag.name
            if tag.moderator_only:
                name = f"{name} [Mod]"
            result.append((tag.id, name))
        return result