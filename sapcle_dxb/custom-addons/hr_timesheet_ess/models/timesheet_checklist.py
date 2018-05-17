from odoo import fields, models, api, _
from datetime import datetime, timedelta
import calendar
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class TimeSheetChecklist(models.Model):
    _name = 'timesheet.checklist'
    _inherit = ['mail.thread']
    _description = 'Business Trip'
    _order = 'year desc'

    MONTHS = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
              (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
              (9, 'September'), (10, 'October'), (11, 'November'),
              (12, 'December')]

    @api.model
    def default_get(self, field_list):
        res = super(TimeSheetChecklist, self).default_get(field_list)
        emp_rec = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        if emp_rec:
            res['employee_id'] = emp_rec.id
        return res

    @api.depends('timesheet_line_ids')
    def _calculate_total_hours(self):
        """
        :return:
        """
        for rec in self:
            total_hour = 0.0
            for line in rec.timesheet_line_ids:
                total_hour += line.unit_amount
            rec.total_timesheet_hours = total_hour

    @api.depends('revised_timesheet_line_ids')
    def _calculate_revised_hours(self):
        """
        :return:
        """
        for rec in self:
            total_hour = 0.0
            for line in rec.revised_timesheet_line_ids:
                total_hour += line.unit_amount
            rec.revised_timesheet_hours = total_hour

    @api.depends('total_timesheet_hours_in_revised', 'revised_timesheet_hours')
    def get_difference(self):
        for rec in self:
            rec.difference_hours = rec.total_timesheet_hours_in_revised - \
                                   rec.revised_timesheet_hours

    @api.depends('difference_hours', 'employee_id')
    def _compute_amount(self):
        """
        :return:
        """
        for rec in self:
            if rec.difference_hours:
                days = rec.difference_hours / 8
                if rec.employee_id and \
                        rec.employee_id.contract_id:
                    rec.amount = (rec.employee_id.contract_id.wage / 30) * days

    name = fields.Char('Doc#', copy=False)
    employee_id = fields.Many2one('hr.employee', "Employee")
    month = fields.Selection(
        MONTHS, string="Month", default=datetime.today().month, copy=False)
    year = fields.Char(string="Year", default=datetime.today().year,
                       copy=False)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('manager_approval', 'Submitted'),
         ('hr_approval', 'Verified'),
         ('approved', 'Approved'),
         ('conflict', 'Conflict'),
         ], string="Status", default='draft', readonly=True)
    ts_projects_ids = fields.One2many(
        'timesheet.projects', 'timesheet_checklist_id', 'Projects', copy=False)
    timesheet_line_ids = fields.One2many(
        'account.analytic.line', 'timesheet_checklist_id', 'Timesheet Lines',
        ondelete='cascade', copy=False)
    is_timesheet_generated = fields.Boolean('Timesheet Generated', copy=False)
    auto_fill = fields.Boolean('Auto Fill Attendance')
    timesheet_checklist_id = fields.Many2one('timesheet.checklist',
                                             'Parent Timesheet')
    total_timesheet_hours = fields.Float('Total Hours',
                                         compute='_calculate_total_hours',
                                         store=True)
    revised_timesheet_line_ids = fields.One2many(
        'revised.timesheet.line', 'timesheet_checklist_id', 'Timesheet Lines',
        ondelete='cascade', copy=False)
    revised_timesheet_hours = fields.Float('Total Hours',
                                           compute='_calculate_revised_hours',
                                           store=True)
    total_timesheet_hours_in_revised = fields.Float(
        'Total Hours', related='timesheet_checklist_id.total_timesheet_hours')
    revision_number = fields.Integer('Revision Number', default=0)
    difference_hours = fields.Float('Difference', compute='get_difference')
    amount = fields.Float('Amount', compute='_compute_amount')
    # child_timesheet_ids = fields.One2many('timesheet.checklist',
    #                                       'timesheet_checklist_id',
    #                                       'Reference')

    @api.multi
    @api.constrains('employee_id', 'month', 'year')
    def _check_validation(self):
        for rec in self:
            tc_rec = self.env['timesheet.checklist'].search([
                ('year', '=', rec.year), ('month', '=', rec.month),
                ('state', '!=', 'conflict'),
                ('id', '!=', rec.id),
                ('employee_id', '=', rec.employee_id.id)])
            if tc_rec:
                raise ValidationError(_('Record Already exist with the same '
                                        'year and month!'))

    @api.model
    def create(self, vals):
        """
        :return:
        """
        if vals:
            if not vals.get('timesheet_checklist_id', False):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'timesheet.checklist')
        res = super(TimeSheetChecklist, self).create(vals)
        return res

    @api.multi
    def unlink(self):
        """
        unlink timesheet line as well
        :return:
        """
        for rec in self:
            for line_rec in rec.timesheet_line_ids:
                line_rec.unlink()
        return super(TimeSheetChecklist, self).unlink()

    @api.multi
    def action_generate_timesheet(self):
        """
        genarate timesheet
        :return:
        """
        analytic_line_obj = self.env['account.analytic.line']
        for rec in self:
            # remove old record and generate new
            rm_list = []
            if rec.timesheet_line_ids:
                for t_line in rec.timesheet_line_ids:
                    t_line.unlink()
            # rec.timesheet_line_ids = rm_list
            # generate new
            for project_rec in rec.ts_projects_ids:
                start_date = datetime.strptime(
                    project_rec.start_date, OE_DATEFORMAT)
                end_date = datetime.strptime(
                    project_rec.end_date, OE_DATEFORMAT)
                day_count = (end_date - start_date).days + 1
                for single_date in [d for d in (
                                start_date + timedelta(n) for n in range(
                    day_count)) if d <= end_date]:
                    records = analytic_line_obj.search([
                        ('user_id', '=', self.env.user.id),
                        ('date', '=', single_date.date()),
                        ('project_id', '=', project_rec.project_id.id or
                         False)])
                    if not records:
                        new_records = analytic_line_obj.create({
                            'name': '',
                            'employee_id': rec.employee_id.id,
                            'date': single_date.date(),
                            'project_id': project_rec.project_id.id,
                            'timesheet_checklist_id': rec.id,
                        })
                        if new_records.week_day in ['Friday', 'Saturday']:
                            new_records.ts_status = 'wo'
                        elif rec.auto_fill:
                            new_records.ts_status = 'fd'
                            new_records.unit_amount = 8
            rec.is_timesheet_generated = True

    @api.multi
    def action_set_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def check_leave_validation(self):
        """
        check leave validation
        :return:
        """
        for rec in self:
            for line in rec.timesheet_line_ids:
                leave_rec = self.env['hr.holidays'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('date_from', '<=', line.date),
                    ('date_to', '>=', line.date),
                    ('type', '=', 'remove'),
                    ('state', 'not in', ['draft', 'cancel', 'refuse'])])
                if leave_rec:
                    if leave_rec.start_day_status == 'half' or \
                                    leave_rec.end_day_status == 'half':
                        if leave_rec.start_day_status == 'half':
                            if leave_rec.date_from.split(' ')[0] == line.date:
                                if line.ts_status != 'hd':
                                    raise ValidationError(
                                        _('You have already applied Half day '
                                          'leave on date %s. Please update '
                                          'attendance status accordingly.') % (
                                            line.date))
                        if leave_rec.end_day_status == 'half':
                            if leave_rec.date_to.split(' ')[0] == line.date:
                                if line.ts_status != 'hd':
                                    raise ValidationError(
                                        _('You have already applied Half day '
                                          'leave on date %s. Please update '
                                          'attendance status accordingly.') % (
                                            line.date))
                    elif line.ts_status != 'l':
                        raise ValidationError(
                            _('You have already applied leave on date %s.'
                              '\n Please update attendance status '
                              'accordingly.')%(line.date))

                if line.ts_status == 'l':
                    if not leave_rec:
                        raise ValidationError(
                            _('No leave Applied for date %s.'
                              '\n Please update attendance status '
                              'accordingly.')%(line.date))

    @api.multi
    def action_submit_to_manager(self):
        for rec in self:
            if not rec.timesheet_line_ids:
                raise ValidationError(_(
                    'You can not submit request without line items !'))
            for line_rec in rec.timesheet_line_ids:
                if not line_rec.ts_status:
                    raise ValidationError(_(
                        'Oops !  Please enter all lines !'))
            rec.check_leave_validation()
            rec.state = 'manager_approval'

    @api.multi
    def action_manager_approval(self):
        for rec in self:
            rec.state = 'hr_approval'

    @api.multi
    def action_hr_approval(self):
        for rec in self:
            existing_attachement = self.env['ir.attachment'].search([
                ('res_id', '=', rec.id), ('res_model', '=', rec._name)])
            if not existing_attachement:
                raise ValidationError(
                    _('You are not allowed to submit the request without'
                      'attaching a document.\n For attaching a document:'
                      'press save then attach a document.'))
            rec.state = 'approved'

    @api.multi
    def action_time_sheet_entry(self):
        #         today = datetime.date.today()
        res_ids = []
        analitic = self.env['account.analytic.line']
        for rec in self:
            if not rec.year or not rec.month:
                raise ValidationError(_('Please Enter Date And Time'))
            days = calendar.monthrange(int(rec.year), int(rec.month))[1]
            for i in range(1, days + 1):
                for_date = datetime.date(
                    int(rec.year), int(rec.month), i).strftime(OE_DATEFORMAT)
                records = analitic.search(
                    [('user_id', '=', self.env.user.id),
                     ('date', '=', for_date),
                     ('project_id', '=',
                      rec.project_id and rec.project_id.id or False)
                     ])

                if not records:
                    records = analitic.create({
                        'project_id': rec.project_id and rec.project_id.id or False,
                        'name': ' ',
                        'date': for_date})
                    res_ids.append(records.id)
                else:
                    res_ids.extend(records.ids)
        res = self.env['ir.actions.act_window'].for_xml_id(
            'hr_timesheet', 'act_hr_timesheet_line')
        res.update({'domain': [('id', 'in', res_ids)]})
        return res

    @api.multi
    def action_generate_revision(self):
        """
        generate timesheet revision
        :return:
        """
        for rec in self:
            rec.state = 'conflict'
            revision_number = rec.revision_number + 1
            name = rec.name + '-R' + str(revision_number)
            ts_projects_ids = []
            for ts_project in rec.ts_projects_ids:
                ts_projects_ids.append((0, 0, {
                    'project_id': ts_project.project_id.id,
                    'start_date': ts_project.start_date,
                    'end_date': ts_project.end_date,
                }))
            timesheet_line_lst = []
            for tl_rec in rec.timesheet_line_ids:
                timesheet_line_lst.append((0, 0, {
                    'project_id': tl_rec.project_id.id,
                    'date': tl_rec.date,
                    'week_day': tl_rec.week_day,
                    'ts_status': tl_rec.ts_status,
                    'unit_amount': tl_rec.unit_amount,
                    'remark': tl_rec.remark,
                }))
            data = {
                'name': name,
                'employee_id': rec.employee_id.id,
                'month': rec.month,
                'year': rec.year,
                'state': 'hr_approval',
                'ts_projects_ids': ts_projects_ids,
                'revised_timesheet_line_ids': timesheet_line_lst,
                'is_timesheet_generated': True,
                'auto_fill': rec.auto_fill,
                'timesheet_checklist_id': rec.id,
                'revision_number': revision_number,
            }
            new_rec = self.create(data)
            return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'timesheet.checklist',
                'res_id': new_rec.id,
                'type': 'ir.actions.act_window'}

    @api.model
    def get_dates(self, m, y):
        """
        :param month:
        :param year:
        :return:
        """
        days = calendar.monthrange(int(y), int(m))
        first_date_s = str(days[0]) + '/' + str(int(m)) + '/' + str(int(y))
        last_date_s = str(days[1]) + '/' + str(int(m)) + '/' + str(int(y))
        return {'f_date': first_date_s, 'l_date': last_date_s}


class TimeSheetProjects(models.Model):
    _name = 'timesheet.projects'
    _description = 'Business Trip'

    project_id = fields.Many2one('project.project', string="Project")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    timesheet_checklist_id = fields.Many2one(
        'timesheet.checklist', 'Timesheet Checklist')

    @api.model
    def default_get(self, fields_list):
        res = super(TimeSheetProjects, self).default_get(fields_list)
        if self._context.get('month') and self._context.get('year'):
            year = str(self._context.get('year'))
            month = str(self._context.get('month'))
            sd = year + '-' + month + '-01'
            s_date = datetime.strptime(sd, OE_DATEFORMAT)
            lday = calendar.monthrange(int(year), int(month))[1]
            ld = year + '-' + month + '-' + str(lday)
            e_date = datetime.strptime(ld, OE_DATEFORMAT)
            res.update({'start_date': s_date, 'end_date': e_date})
        return res

    @api.constrains('start_date', 'end_date')
    def check_date_validation(self):
        for rec in self:
            if rec.timesheet_checklist_id:
                month = int(rec.timesheet_checklist_id.month)
                year = int(rec.timesheet_checklist_id.year)
                s_date = datetime.strptime(rec.start_date, OE_DATEFORMAT)
                e_date = datetime.strptime(rec.end_date, OE_DATEFORMAT)
                if month != s_date.month or month != e_date.month or year != \
                        s_date.year or year != e_date.year:
                    raise ValidationError(_('please select a valid date )'))
            domain = [
                ('start_date', '<=', rec.end_date),
                ('end_date', '>=', rec.start_date),
                ('id', '!=', rec.id),
                ('timesheet_checklist_id', '=', rec.timesheet_checklist_id.id)]
            overleps_rec = self.search_count(domain)
            if overleps_rec:
                raise ValidationError(_(
                    'You can not have 2 projects that overlaps on same day!'))

class AccountAnalyticLine(models.Model):
    _inherit='account.analytic.line'

    remark = fields.Text('Remark')

class RevisedTimesheetLine(models.Model):
    _name = 'revised.timesheet.line'

    project_id = fields.Many2one('project.project', 'Project')
    date = fields.Date('Date')
    week_day = fields.Char(string="Day")
    ts_status = fields.Selection([
        ('fd', 'Full Day'), ('hd', 'Half Day'), ('wo', 'Week Off'),
        ('l', 'Leave'), ('ph', 'Public Holiday')], string="Attendance")
    unit_amount = fields.Float('Quantity')
    remark = fields.Text('Remark')
    timesheet_checklist_id = fields.Many2one(
        'timesheet.checklist', string='Timesheet Checklist')

    @api.onchange('ts_status')
    def onchange_status(self):
        for rec in self:
            if rec.ts_status == 'fd':
                rec.unit_amount = 8.00
            elif rec.ts_status == 'hd':
                rec.unit_amount = 4.00
            elif rec.ts_status == 'wo':
                rec.unit_amount = 0.00
            elif rec.ts_status == 'l':
                rec.unit_amount = 0.00
            elif rec.ts_status == 'ph':
                rec.unit_amount = 8.00
            else:
                rec.unit_amount = 0.00