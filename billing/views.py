from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .models import * #el astericos importa todo(cuando se que trabajare con todos los que esta en esa clase)
from .forms import SignUpForm, BrandForm, InvoiceForm, InvoiceDetailFormSet, ProductForm
from decimal import Decimal
from django.core.paginator import Paginator
from .export_mixins import ExportMixin
from django.db import models
from shared.mixins import StaffRequiredMixin
from shared.decorators import audit_action


# === HOME (Página principal) ===
@login_required
def home(request):
    """Vista principal del sistema. Muestra resumen general."""
    context = {
        'total_brands': Brand.objects.count(),
        'total_products': Product.objects.count(),
        'total_customers': Customer.objects.count(),
        'total_invoices': Invoice.objects.count(),
        'recent_invoices': Invoice.objects.all()[:5],  # Últimas 5
        'low_stock': Product.objects.filter(stock__lte=5, is_active=True),
    }
    return render(request, 'billing/home.html', context)

# === REGISTRO ===
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('billing:brand_list')
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

# === BRAND (FBV) ===
@login_required
@audit_action('LIST_BRANDS')
def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'billing/brand_list.html', {'brands': brands})

@login_required
@audit_action('CREATE_BRAND')
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand created!')
            return redirect('billing:brand_list')
    else: form = BrandForm()
    return render(request, 'billing/brand_form.html', {'form':form, 'title':'Crear marca'})

@login_required
@audit_action('UPDATE_BRAND')
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand updated!')
            return redirect('billing:brand_list')
    else: form = BrandForm(instance=brand)
    return render(request, 'billing/brand_form.html', {'form':form, 'title':'Ediatr Marca'})

@login_required
@audit_action('DELETE_BRAND')
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, 'Marca borrada!')
        return redirect('billing:brand_list')
    return render(request, 'billing/brand_confirm_delete.html', {'object': brand})

class ProductGroupListView(LoginRequiredMixin, ListView):
    model = ProductGroup
    template_name = 'billing/productgroup_list.html'
    context_object_name = 'items'

class ProductGroupCreateView(LoginRequiredMixin, CreateView):
    model = ProductGroup
    fields = ['name', 'is_active']
    template_name = 'billing/productgroup_form.html'
    success_url = reverse_lazy('billing:productgroup_list')

class ProductGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductGroup
    fields = ['name', 'is_active']
    template_name = 'billing/productgroup_form.html'
    success_url = reverse_lazy('billing:productgroup_list')

class ProductGroupDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ProductGroup
    template_name = 'billing/productgroup_confirm_delete.html'
    success_url = reverse_lazy('billing:productgroup_list')
    staff_redirect_url = '/groups/'

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'billing/supplier_list.html'
    context_object_name = 'items'

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    fields = ['name', 'contact_name', 'email', 'phone', 'address', 'is_active']
    template_name = 'billing/supplier_form.html'
    success_url = reverse_lazy('billing:supplier_list')

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    fields = ['name', 'contact_name', 'email', 'phone', 'address', 'is_active']
    template_name = 'billing/supplier_form.html'
    success_url = reverse_lazy('billing:supplier_list')

class SupplierDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'billing/supplier_confirm_delete.html'
    success_url = reverse_lazy('billing:supplier_list')
    staff_redirect_url = '/suppliers/'

@login_required
def product_list(request):
    # ── Individual filter fields ──────────────────────────────
    f_name         = request.GET.get('name', '').strip()
    f_description  = request.GET.get('description', '').strip()
    f_brand        = request.GET.get('brand', '')
    f_group        = request.GET.get('group', '')
    f_supplier     = request.GET.get('supplier', '')
    f_min_price    = request.GET.get('min_price', '').strip()
    f_max_price    = request.GET.get('max_price', '').strip()
    f_min_stock    = request.GET.get('min_stock', '').strip()
    f_max_stock    = request.GET.get('max_stock', '').strip()
    f_stock_status = request.GET.get('stock_status', '')
    f_is_active    = request.GET.get('is_active', '')

    items = Product.objects.select_related('brand', 'group').prefetch_related('suppliers').all()

    if f_name:
        items = items.filter(name__icontains=f_name)
    if f_description:
        items = items.filter(description__icontains=f_description)
    if f_brand:
        items = items.filter(brand_id=f_brand)
    if f_group:
        items = items.filter(group_id=f_group)
    if f_supplier:
        items = items.filter(suppliers__id=f_supplier)
    if f_min_price:
        items = items.filter(unit_price__gte=f_min_price)
    if f_max_price:
        items = items.filter(unit_price__lte=f_max_price)
    if f_min_stock:
        items = items.filter(stock__gte=f_min_stock)
    if f_max_stock:
        items = items.filter(stock__lte=f_max_stock)
    if f_stock_status == 'out':
        items = items.filter(stock=0)
    elif f_stock_status == 'low':
        items = items.filter(stock__gt=0, stock__lte=10)
    elif f_stock_status == 'available':
        items = items.filter(stock__gt=0)
    if f_is_active == '1':
        items = items.filter(is_active=True)
    elif f_is_active == '0':
        items = items.filter(is_active=False)

    items = items.distinct()

    # ── Export ────────────────────────────────────────────────
    export = request.GET.get('export', '')
    if export in ('pdf', 'excel'):
        exporter = ExportMixin()
        exporter.export_filename = 'productos'
        exporter.export_title = 'Listado de Productos'
        exporter.export_headers = ['Nombre', 'Descripcion', 'Marca', 'Grupo', 'Precio', 'Stock', 'Proveedores', 'Activo']
        exporter.get_export_rows = lambda qs: [
            [
                p.name,
                p.description or '-',
                p.brand.name,
                p.group.name,
                f'${p.unit_price}',
                p.stock,
                ', '.join(s.name for s in p.suppliers.all()) or '-',
                'Si' if p.is_active else 'No',
            ]
            for p in qs
        ]
        if export == 'pdf':
            return exporter.export_to_pdf(items)
        else:
            return exporter.export_to_excel(items)

    # ── Pagination ────────────────────────────────────────────
    total_count = items.count()
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    get_params = request.GET.copy()
    get_params.pop('page', None)
    get_params.pop('export', None)
    filter_querystring = get_params.urlencode()

    context = {
        'page_obj': page_obj,
        'total_count': total_count,
        'filter_querystring': filter_querystring,
        'f_name': f_name,
        'f_description': f_description,
        'selected_brand': f_brand,
        'selected_group': f_group,
        'selected_supplier': f_supplier,
        'min_price': f_min_price,
        'max_price': f_max_price,
        'min_stock': f_min_stock,
        'max_stock': f_max_stock,
        'stock_status': f_stock_status,
        'is_active': f_is_active,
        'brands': Brand.objects.filter(is_active=True),
        'groups': ProductGroup.objects.filter(is_active=True),
        'suppliers': Supplier.objects.filter(is_active=True),
    }
    return render(request, 'billing/product_list.html', context)

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'billing/product_form.html'
    success_url = reverse_lazy('billing:product_list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'billing/product_form.html'
    success_url = reverse_lazy('billing:product_list')

class ProductDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Product
    template_name = 'billing/product_confirm_delete.html'
    success_url = reverse_lazy('billing:product_list')
    staff_redirect_url = '/products/'

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'billing/customer_list.html'
    context_object_name = 'items'

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    fields = ['dni', 'first_name', 'last_name', 'email', 'phone', 'address', 'is_active']
    template_name = 'billing/customer_form.html'
    success_url = reverse_lazy('billing:customer_list')

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    fields = ['dni', 'first_name', 'last_name', 'email', 'phone', 'address', 'is_active']
    template_name = 'billing/customer_form.html'
    success_url = reverse_lazy('billing:customer_list')

class CustomerDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Customer
    template_name = 'billing/customer_confirm_delete.html'
    success_url = reverse_lazy('billing:customer_list')
    staff_redirect_url = '/customers/'

@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('customer').all()
    return render(request, 'billing/invoice_list.html', {'items': invoices})

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceDetailFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.save()
            formset.instance = invoice
            formset.save()
            subtotal = sum(d.subtotal for d in invoice.details.all())
            invoice.subtotal = subtotal
            invoice.tax = subtotal * Decimal('0.15')
            invoice.total = invoice.subtotal + invoice.tax
            invoice.save()
            messages.success(request, f'Invoice #{invoice.id} created! Total: ${invoice.total}')
            return redirect('billing:invoice_list')
    else:
        form = InvoiceForm()
        formset = InvoiceDetailFormSet()
    return render(request, 'billing/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Invoice',
    })

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('customer').prefetch_related('details__product'),
        pk=pk
    )
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice})

@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice_id = invoice.id
        invoice.delete()
        messages.success(request, f'Invoice #{invoice_id} deleted!')
        return redirect('billing:invoice_list')
    return render(request, 'billing/invoice_confirm_delete.html', {'object': invoice})
