{
    'name': 'StackIt Q&A Forum',
    'version': '1.0.0',
    'summary': 'StackOverflow-like Question & Answer Platform',
    'description': """
        Complete Q&A Forum System with:
        - Questions and Answers
        - Voting System
        - Tagging
        - User Profiles
        - Real-time Notifications
    """,
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'category': 'Website/Forum',
    'depends': [
        'website',
        'web_editor',
        'mail',
        'portal',
        'auth_signup'
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        
        # Data
        'data/tag_data.xml',
        'data/mail_template_data.xml',
        
        # Models
        'models/question.py',
        'models/answer.py',
        'models/tag.py',
        'models/vote.py',
        'models/user.py',
        
        # Views
        'views/question_views.xml',
        'views/answer_views.xml',
        'views/tag_views.xml',
        'views/user_views.xml',
        'views/templates.xml',
        'views/menus.xml',
        
        # Controllers
        'controllers/main.py',
        
        # Assets
        'views/assets.xml'
    ],
    'demo': [
        'demo/demo_data.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'stackit_odoo_hackathon/static/src/scss/style.scss',
            'stackit_odoo_hackathon/static/src/js/voting.js',
            'stackit_odoo_hackathon/static/src/js/notifications.js',
            'stackit_odoo_hackathon/static/src/js/rich_text.js',
        ],
        'web.assets_backend': [
            'stackit_odoo_hackathon/static/src/scss/backend.scss',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'price': 0.00,
    'currency': 'USD',
}