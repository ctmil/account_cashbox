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

	@api.multi
	def unlink(self):
        	for line in self:
			if line.move_id:
				self.env['account.move'].button_cancel(line.move_id.id)
	        return super(account_cashbox_lines, self).unlink()

	@api.multi
	def write(self,vals):
		for line in self:
			if line.move_id:
				if line.line_type == 'substract' and line.amount > 0:
                        		raise osv.except_osv(('Error'),\
						 ('El monto debe ser negativo para retiros de dinero de la caja'))
		                        return None
				if line.line_type == 'add' and line.amount < 0:
                        		raise osv.except_osv(('Error'),\
						 ('El monto debe ser positivo para operaciones de agregado de dinero a la caja'))
		                        return None
				
				
			        settings = self.env['account.cashbox.settings'].search([])
        		        if not settings:
                        		raise osv.except_osv(('Error'), ('No hay configuracion definida'))
		                        return None
                		period_id = line.move_id.period_id
				#self.env['account.move'].button_cancel(line.move_id.id)
				line.move_id.button_cancel()
				if line.line_type == 'add':
			                vals_account_move = {
                			        'date': line.date,
		        	                'period_id': line.period_id.id,
                			        'journal_id': settings.cashbox_journal.id,
			                        'ref': line.name,
                			        'narration': line.name,
		                	        }
	                		move_id = self.env['account.move'].create(vals_account_move)
				        vals_account_move_line_debit = {
			                        'account_id': settings.cashbox_account.id,
		        	                'debit': line.amount,
                			        'credit': 0,
			                        'date': line.date,
        	        		        'journal_id': settings.cashbox_journal.id,
			                        'name': line.name,
                			        'narration': line.name,
		                	        'move_id': move_id.id,
                		        	'period_id': period_id.id,
			                        #'analytic_account_id': self.analytic_account_id.id,
        	        		        }
			                line_debit_id = self.env['account.move.line'].create(vals_account_move_line_debit)
        	        		vals_account_move_line_credit = {
			                        'account_id': line.account.id,
                			        'debit': 0,
		                	        'credit': line.amount,
                		        	'date': line.date,
			                        'journal_id': settings.cashbox_journal.id,
        	        		        'name': line.name,
                	        		'narration': line.name,
		        	                'move_id': move_id.id,
                			        'period_id': period_id.id,
		                        	'analytic_account_id': line.analytic_account_id.id,
	                		        }	
			                line_credit_id = self.env['account.move.line'].create(vals_account_move_line_credit)
                			move_id.button_validate()
		                	vals = {
                			        'move_id': move_id.id,
		                        	}
	                		line.write(vals)
				else:
			               # Creates accounting move
			                vals_account_move = {
			                        'date': line.date,
                        			'period_id': period_id.id,
			                        'journal_id': settings.cashbox_journal.id,
			                        'ref': line.name,
                        			'narration': line.name,
			                        }
					move_id = self.env['account.move'].create(vals_account_move)
			                vals_account_move_line_credit = {
                        			'account_id': settings.cashbox_account.id,
			                        'credit': line.amount * (-1),
                        			'debit': 0,
			                        'date': line.date,
                        			'journal_id': settings.cashbox_journal.id,
			                        'name': line.name,
                        			'narration': line.name,
			                        'move_id': move_id.id,
                        			'period_id': period_id.id,
			                        #'analytic_account_id': self.analytic_account_id.id,
                        			}
			                line_credit_id = self.env['account.move.line'].create(vals_account_move_line_credit)
			                vals_account_move_line_debit = {
                        			'account_id': line.account_id.id,
			                        'debit': line.amount * (-1),
                        			'credit': 0,
			                        'date': line.date,
                        			'journal_id': settings.cashbox_journal.id,
			                        'name': line.name,
                        			'narration': line.name,
			                        'move_id': move_id.id,
                        			'period_id': period_id.id,
			                        'analytic_account_id': line.analytic_account_id.id,
                        			}
			                line_debit_id = self.env['account.move.line'].create(vals_account_move_line_debit)
			                move_id.button_validate()
			                vals = {	
                        			'move_id': move_id.id,
			                        }
			                line.write(vals)
		return None

				


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
	state = fields.Selection(selection=[('posted','Publicado'),('cancel','Cancelado')],string='Estado')


class account_cashbox_settings(models.Model):
        _name = 'account.cashbox.settings'

	name = fields.Char('Nombre')
	expense_account = fields.Many2one('account.account',string='Cuenta de gastos')
	income_account = fields.Many2one('account.account',string='Cuenta de ingresos')
	cashbox_account = fields.Many2one('account.account',string='Cuenta de caja')
	bank_account = fields.Many2one('account.account',string='Cuenta de banco')
	cashbox_journal = fields.Many2one('account.journal',string='Diario de caja')

class account_invoice(models.Model):
        _inherit = 'account.invoice'

	@api.one
	def _compute_mes_factura(self):
		if self.date_invoice:
			self.mes_factura = self.date_invoice[:7]

	def _search_mes_factura(self,operator,value):
		return [('date_invoice','like',value)]

	mes_factura = fields.Char(string='Mes factura',compute=_compute_mes_factura,search=_search_mes_factura)
