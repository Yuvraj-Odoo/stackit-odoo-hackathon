# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request, route
from odoo.addons.website.controllers.main import QueryURL
from werkzeug.exceptions import NotFound, Forbidden
import logging

_logger = logging.getLogger(__name__)

class StackItController(http.Controller):

    # Helper Methods
    def _get_question_domain(self, filter_type=None):
        domain = [('active', '=', True)]
        if filter_type == 'unanswered':
            domain.append(('answer_count', '=', 0))
        elif filter_type == 'newest':
            domain.append(('create_date', '!=', False))
        return domain

    def _prepare_question_values(self, question=None, **kwargs):
        values = {
            'question': question,
            'user': request.env.user,
            'tags': request.env['stackit.tag'].search([('active', '=', True)]),
            'filters': {
                'newest': _('Newest'),
                'unanswered': _('Unanswered'),
            },
            'url': QueryURL('/questions', **kwargs),
        }
        return values

    # Main Routes
    @route('/questions', type='http', auth="public", website=True)
    def questions_page(self, filter_type=None, **kwargs):
        domain = self._get_question_domain(filter_type)
        questions = request.env['stackit.question'].search(
            domain,
            order='create_date desc' if filter_type == 'newest' else 'vote_count desc'
        )
        values = self._prepare_question_values(**kwargs)
        values.update({
            'questions': questions,
            'current_filter': filter_type,
        })
        return request.render("stackit_odoo_hackathon.questions_page", values)

    @route('/question/<int:question_id>', type='http', auth="public", website=True)
    def question_detail(self, question_id, **kwargs):
        question = request.env['stackit.question'].browse(question_id).sudo()
        if not question.exists():
            raise NotFound()
        
        question.increment_view_count()
        values = self._prepare_question_values(question=question, **kwargs)
        return request.render("stackit_odoo_hackathon.question_detail", values)

    @route('/ask', type='http', auth="user", website=True)
    def ask_question(self, **kwargs):
        values = self._prepare_question_values(**kwargs)
        return request.render("stackit_odoo_hackathon.ask_question", values)

    @route('/question/<int:question_id>/answer', type='http', auth="user", methods=['POST'], website=True)
    def post_answer(self, question_id, content, **kwargs):
        question = request.env['stackit.question'].browse(question_id)
        if not question.exists():
            raise NotFound()
        
        if not content:
            raise Forbidden(_("Answer cannot be empty"))
        
        request.env['stackit.answer'].create({
            'question_id': question.id,
            'content': content,
        })
        return request.redirect(f"/question/{question_id}")

    @route('/vote', type='json', auth="user")
    def process_vote(self, question_id=None, answer_id=None, is_upvote=True):
        Vote = request.env['stackit.vote']
        vote_type = 'upvote' if is_upvote else 'downvote'
        
        if question_id:
            record = request.env['stackit.question'].browse(question_id)
            existing = Vote.search([
                ('user_id', '=', request.uid),
                ('question_id', '=', question_id)
            ])
        elif answer_id:
            record = request.env['stackit.answer'].browse(answer_id)
            existing = Vote.search([
                ('user_id', '=', request.uid),
                ('answer_id', '=', answer_id)
            ])
        else:
            return {'error': _("Invalid voting target")}

        if not record.exists():
            return {'error': _("Content not found")}

        if existing:
            existing.write({'vote_type': vote_type})
        else:
            Vote.create({
                'vote_type': vote_type,
                'user_id': request.uid,
                'question_id': question_id,
                'answer_id': answer_id,
            })

        return {
            'new_score': record.vote_count,
            'message': _("Vote recorded")
        }

    @route('/accept_answer', type='json', auth="user")
    def accept_answer(self, answer_id):
        answer = request.env['stackit.answer'].browse(answer_id)
        if not answer.exists():
            return {'error': _("Answer not found")}
        
        if request.uid != answer.question_id.user_id.id:
            return {'error': _("Only the question owner can accept answers")}
        
        answer.action_accept_answer()
        return {'success': True}

    # Utility Routes
    @route('/questions/tag/<string:tag_name>', type='http', auth="public", website=True)
    def questions_by_tag(self, tag_name, **kwargs):
        tag = request.env['stackit.tag'].search([('name', '=', tag_name)], limit=1)
        if not tag:
            raise NotFound()
        
        questions = request.env['stackit.question'].search([
            ('tag_ids', 'in', tag.id),
            ('active', '=', True)
        ])
        values = self._prepare_question_values(**kwargs)
        values.update({
            'questions': questions,
            'current_tag': tag,
        })
        return request.render("stackit_odoo_hackathon.questions_page", values)

    @route('/notifications', type='json', auth="user")
    def get_notifications(self):
        notifications = request.env['stackit.notification'].search([
            ('user_id', '=', request.uid),
            ('is_read', '=', False)
        ], order='create_date desc', limit=10)
        
        return [{
            'id': n.id,
            'message': n.message,
            'type': n.notification_type,
            'date': fields.Datetime.to_string(n.create_date),
            'question_id': n.related_question_id.id,
        } for n in notifications]