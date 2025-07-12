odoo.define('stackit.rich_text', function(require) {
"use strict";

var publicWidget = require('web.public.widget');
var wysiwyg = require('web_editor.wysiwyg');

publicWidget.registry.StackItRichText = publicWidget.Widget.extend({
    selector: '.stackit-rich-text',
    start: function() {
        var self = this;
        this.$el.find('textarea').each(function() {
            var $textarea = $(this);
            var editor = new wysiwyg.Editor($textarea, {
                toolbar: [
                    ['style', ['bold', 'italic', 'underline', 'clear']],
                    ['font', ['strikethrough']],
                    ['para', ['ul', 'ol', 'paragraph']],
                    ['insert', ['link', 'picture']],
                    ['misc', ['codeview', 'help']]
                ],
                airMode: false,
                styleWithSpan: false,
                callbacks: {
                    onInit: function() {
                        $textarea.closest('form').on('submit', function() {
                            $textarea.val(editor.getValue());
                        });
                    },
                    onImageUpload: function(files) {
                        self._uploadImage(files[0], editor);
                    }
                }
            });
        });
    },

    _uploadImage: function(file, editor) {
        var formData = new FormData();
        formData.append('file', file);
        formData.append('csrf_token', odoo.csrf_token);

        $.ajax({
            url: '/stackit/upload_image',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                if (data.url) {
                    editor.insertImage(data.url);
                }
            }
        });
    }
});

return publicWidget.registry.StackItRichText;
});