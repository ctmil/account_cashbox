from openerp import models, api, fields
from openerp.exceptions import except_orm, Warning, RedirectWarning

class account_cashbox(models.Model):
	_name = 'account.cashbox'

	@api.one
	def _compute_total_amount(self):
		total_amount = 0
		for line in self.cashbox_lines:
			total_amount = total_amount + line.amount
		self.total_amount = total_amount

	name = fields.Char(string='Nombre')
	# date = fields.Date(string='Fecha')
	cashbox_lines = fields.One2many(comodel_name='account.cashbox.lines',inverse_name='cashbox_id')
	total_amount = fields.Float(string='Monto Caja',readonly=True,compute=_compute_total_amount)

	@api.multi
	def cashbox_add_line(self):
                return {'type': 'ir.actions.act_window',
                        'name': 'Add line to cashbox',
                        'res_model': 'account.cashbox.add.line',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'target': 'new',
                        'nodestroy': True,
                        }

	@api.multi
	def cashbox_substract_line(self):
                return {'type': 'ir.actions.act_window',
                        'name': 'Substract line from cashbox',
                        'res_model': 'account.cashbox.substract.line',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'target': 'new',
                        'nodestroy': True,
                        }

class account_cashbox_lines(models.Model):
	_name = 'account.cashbox.lines'

	name = fields.Char(string='Concepto')
	cashbox_id = fields.Many2one('account.cashbox',string='Caja')
	cashbox_name = fields.Char('Caja',related='cashbox_id.name')
	date = fields.Date(string='Fecha')
	line_type = fields.Selection(selection=[('add','Agregar'),('substract','Sacar')],string='Tipo Operacion')
	amount = fields.Float(string='Monto')	
	move_id = fields.Many2one('account.move')
	check_id = fields.Many2one('account.check')
	analytic_account_id = fields.Many2one('account.analytic.account',string='Centro de costos')
	account_id = fields.Many2one('account.account',string='Cuenta de gastos')


class account_cashbox_settings(models.Model):
        _name = 'account.cashbox.settings'

	name = fields.Char('Nombre')
	expense_account = fields.Many2one('account.account',string='Cuenta de gastos')
	income_account = fields.Many2one('account.account',string='Cuenta de ingresos')
	cashbox_account = fields.Many2one('account.account',string='Cuenta de caja')
	bank_account = fields.Many2one('account.account',string='Cuenta de banco')
	cashbox_journal = fields.Many2one('account.journal',string='Diario de caja')
