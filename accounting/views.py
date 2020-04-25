# Copyright (c) 2015-2022 Data King Ltd
# See LICENSE file for license details

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from datetime import date

from .models import *


class ReportView(TemplateView):

    def get_context_data(self, **kwargs):
        res = super(ReportView, self).get_context_data(**kwargs)
        fy = kwargs['fy']

        try:
            y = int(fy)
            i = 0
        except ValueError:
            y = int(fy[:-1])
            i = ord(fy[-1]) - 64

        try:
            fy = FiscalYear.objects.filter(
                end__gte=date(y, 1, 1), end__lte=date(y, 12, 31)
            ).order_by('end')[i]
        except IndexError:
            raise Http404

        res['fy'] = fy
        res['title'] = '{} {}'.format(self.title, fy)
        self.update_context(res, kwargs)
        return res


class AccountView(ReportView):

    def update_context(self, context, args):
        context['accounts'] = Account.objects.all()

class AccountChartView(AccountView):
    title = 'Chart of Accounts'
    template_name = 'accounting/account_chart.html'

class GeneralLedgerView(AccountView):
    title = 'General Ledger'
    template_name = 'accounting/general_ledger.html'


class JournalView(ReportView):
    title = 'General Journal'
    template_name = 'accounting/journal.html'

    def update_context(self, context, args):
        txn_filter = {'fiscal_year': context['fy']}

        if 'code' in args:
            journal = get_object_or_404(Journal, code=args['code'])
            context['title'] = journal.description or journal.code
            txn_filter['journal'] = journal

        context['transactions'] = Transaction.objects.filter(**txn_filter)


class AnnualReportView(AccountChartView):

    def update_context(self, context, args):
        context['accounts'] = Account.objects.filter(
            type__in=self.account_types
        )
        context['include_closing'] = 'NE' in self.account_types

class BalanceSheetView(AnnualReportView):
    title = 'Balance Sheet'
    account_types = ('As', 'Eq', 'NE', 'Li')

class IncomeStatementView(AnnualReportView):
    title = 'Income Statement'
    account_types = ('In', 'Ex')
