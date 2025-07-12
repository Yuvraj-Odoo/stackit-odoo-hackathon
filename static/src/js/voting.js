odoo.define('stackit.voting', function(require) {
"use strict";

var publicWidget = require('web.public.widget');
var ajax = require('web.ajax');
var core = require('web.core');
var _t = core._t;

publicWidget.registry.StackItVoting = publicWidget.Widget.extend({
    selector: '.vote-block',
    events: {
        'click .vote-up': '_onVoteUp',
        'click .vote-down': '_onVoteDown',
    },

    start: function() {
        this._super.apply(this, arguments);
        this._bindTooltips();
    },

    _bindTooltips: function() {
        this.$el.find('[data-toggle="tooltip"]').tooltip({
            trigger: 'hover',
            placement: 'top'
        });
    },

    _onVoteUp: function(ev) {
        this._vote(ev, true);
    },

    _onVoteDown: function(ev) {
        this._vote(ev, false);
    },

    _vote: function(ev, isUpvote) {
        ev.preventDefault();
        ev.stopPropagation();

        var $target = $(ev.currentTarget);
        var answerId = this.$el.data('answer-id');
        var questionId = this.$el.data('question-id');

        if (!this._validateUser()) {
            return;
        }

        this._showLoading($target);

        ajax.jsonRpc('/stackit/vote', 'call', {
            question_id: questionId,
            answer_id: answerId,
            is_upvote: isUpvote,
        }).then(function(data) {
            if (data.error) {
                this._showError(data.error);
            } else {
                this.$el.find('.vote-count').text(data.new_score);
                this._highlightVote($target, isUpvote);
            }
        }.bind(this)).catch(function() {
            this._showError(_t("Voting failed. Please try again."));
        }.bind(this)).finally(function() {
            this._hideLoading($target);
        }.bind(this));
    },

    _validateUser: function() {
        if (!odoo.session_info.user_id) {
            this._showError(_t("Please login to vote"));
            return false;
        }
        return true;
    },

    _showLoading: function($element) {
        $element.addClass('fa-spin');
    },

    _hideLoading: function($element) {
        $element.removeClass('fa-spin');
    },

    _highlightVote: function($element, isUpvote) {
        this.$el.find('.vote-up, .vote-down').removeClass('text-success text-danger');
        $element.addClass(isUpvote ? 'text-success' : 'text-danger');
    },

    _showError: function(message) {
        var $notif = $('<div class="alert alert-danger">').text(message);
        this.$el.before($notif);
        setTimeout(function() {
            $notif.fadeOut(500, function() { $(this).remove(); });
        }, 3000);
    },
});

return publicWidget.registry.StackItVoting;
});