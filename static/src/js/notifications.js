odoo.define('stackit.notifications', function(require) {
"use strict";

var publicWidget = require('web.public.widget');
var ajax = require('web.ajax');
var core = require('web.core');
var _t = core._t;

publicWidget.registry.StackItNotifications = publicWidget.Widget.extend({
    selector: '#notification-bell',
    events: {
        'click': '_onClickBell',
    },

    start: function() {
        this._super.apply(this, arguments);
        this._pollNotifications();
        this._setupBadge();
    },

    _pollNotifications: function() {
        if (!odoo.session_info.user_id) return;

        setInterval(function() {
            this._fetchNotifications();
        }.bind(this), 30000); // Poll every 30 seconds
    },

    _setupBadge: function() {
        this._fetchNotifications();
    },

    _fetchNotifications: function() {
        ajax.jsonRpc('/stackit/notifications', 'call').then(function(notifications) {
            var unreadCount = notifications.filter(n => !n.is_read).length;
            this.$el.find('.badge').text(unreadCount || '');
            
            if (unreadCount > 0) {
                this.$el.addClass('has-unread');
            } else {
                this.$el.removeClass('has-unread');
            }
        }.bind(this));
    },

    _onClickBell: function(ev) {
        ev.preventDefault();
        
        ajax.jsonRpc('/stackit/notifications/mark_read', 'call').then(function() {
            this._fetchNotifications();
            this._showDropdown();
        }.bind(this));
    },

    _showDropdown: function() {
        var $dropdown = this.$el.next('.dropdown-menu');
        $dropdown.empty();
        
        ajax.jsonRpc('/stackit/notifications', 'call').then(function(notifications) {
            if (notifications.length === 0) {
                $dropdown.append($('<li>').text(_t("No notifications")));
                return;
            }

            notifications.forEach(function(notif) {
                var $item = $('<li>').addClass('notification-item');
                var $link = $('<a>')
                    .attr('href', '#')
                    .data('question-id', notif.question_id)
                    .text(notif.message);
                
                $item.append($link);
                $dropdown.append($item);
            });

            $dropdown.find('.notification-item a').click(function(ev) {
                ev.preventDefault();
                var questionId = $(this).data('question-id');
                window.location.href = '/question/' + questionId;
            });
        });
    }
});

return publicWidget.registry.StackItNotifications;
});