@extends('layouts.sidebar_daily_credit')

@section('content-wrapper')
<div class="content-wrapper">
  <!-- Content Header (Page header) -->
  <section class="content-header">
    <div class="container-fluid">
      <div class="row mb-2">
        <div class="col-sm-6">
          <h1>Daftar Nasabah Kredit Harian</h1>
        </div>
      </div>
    </div><!-- /.container-fluid -->
  </section>

  <!-- Main content -->
  <section class="content">
      <div class="container-fluid">
        <div class="row">
          <div class="col-12">
            <div class="card">
              <div class="card-body">
                <div class="table-responsive">
                  <table class="table table-bordered yajra-datatable">
                    <thead>
                      <tr>
                        <th>No</th>
                        <th>NO.SPP</th>
                        <th>Nama</th>
                        <th>Alamat</th>
                        <th>Kolektor</th>
                        <th>Jml Pinjaman(Rp.)</th>
                        <th>Sisa Pinjaman</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                    </tbody>
                  </table>
                </div>
              </div>
              <!-- /.card-body -->
              <div class="card-footer clearfix">
                <a href="#" class="btn btn-sm btn-info float-left" id="myButton">Export to Excel</a>
              </div>
            </div>
            <!-- /.card -->
          </div>
          <!-- /.col -->
        </div>
        <!-- /.row -->
      </div>
      <!-- /.container-fluid -->
    </section>
  <!-- /.content -->
</div>
@endsection

@section('js')
<script>
  $(function () {
    
    var table = $('.yajra-datatable').DataTable({
        processing: true,
        serverSide: true,
        ajax: "{{ route('dailycredit.list') }}",
        columns: [
            {
              data: 'id', name: 'id',
              render: function(data, type) {
                  html = `
                        <span><a href='/daily_credit/${data}')' data-toggle='tooltip' data-placement='top' title='Detail'>${data}</span>
                        ` 
                  return html;
              }
            },
            {data: 'noSPP', name: 'noSPP'},
            {data: 'name', name: 'name'},
            {data: 'address', name: 'address'},
            {data: 'collector', name: 'collector'},
            {data: 'allowance', name: 'allowance',},
            {data: 'installment', name: 'installment'},
            {
              data: 'id', 
              name: 'id',
              render: function(data, type) {
                  html = `
                        <a href='/daily_credit/${data}/pay')' data-toggle='tooltip' data-placement='top' title='Payment'>
                        <i class="fas fa-wallet"></i></a>
                        <a href='/daily_credit/${data}/edit')' data-toggle='tooltip' data-placement='top' title='Edit'>
                        <i class='fa fa-edit fa-action'></i></a>
                        <a href='/daily_credit/${data}/destroy')' data-toggle='tooltip' data-placement='top' title='Delete'>
                        <i class='fa fa-trash-alt fa-action'></i></a>
                        `
                     
                    return html;
              }
            }
        ]
    });
    
  });
</script>
<script>
  $(document).ready(function(e){
    $("#myButton").click(function(e){

      $(".yajra-datatable").table2excel({

        name:"Worksheet Name",

        filename:"Kredit_Harian",//do not include extension

        fileext:".xls" // file extension

      });

    });

  });

</script>
@endsection