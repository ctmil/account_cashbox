# -*- coding: utf-8 -*-
##############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools.safe_eval import safe_eval as eval

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class account_cashbox_lines(osv.osv):
	_inherit = "account.cashbox.lines"

	def unlink(self, cr, uid, ids, context=None):
		#self._check_moves(cr, uid, ids, "unlink", context=context)
		for line_id in ids:
			cashbox_line = self.pool.get('account.cashbox.lines').browse(cr,uid,line_id)
			if cashbox_line.move_id:
				return_id = self.pool.get('account.move').button_cancel(cr,uid,[cashbox_line.move_id.id])
				if return_id:
					return_id = self.pool.get('account.move').unlink(cr,uid,cashbox_line.move_id.id)
		return super(account_cashbox_lines, self).unlink(cr, uid, ids, context=context)


	def onchange_analytical_account_id(self, cr, uid, ids, analytic_account_id=None, context=None):
		for line_id in ids:
			if analytic_account_id:
				line = self.pool.get('account.cashbox.lines').browse(cr,uid,line_id)
				vals = {
					'analytic_account_id': analytic_account_id,
					}
				return_id = self.pool.get('account.cashbox.lines').write(cr,uid,line_id,vals)
				if line.move_id:
					vals_move ={
						'analytic_account_id': analytic_account_id,
						}
					for move_line_id in line.move_id.line_id:
						return_id = self.pool.get('account.move.line').write(cr,uid,move_line_id,vals_move)

