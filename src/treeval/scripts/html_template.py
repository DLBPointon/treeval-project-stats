html_string = '''
    <html>
        <head>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">
            <style>
                body{
                    margin:0 100;
                    background:whitesmoke;
                }
                .boxy{
                    float: left;
                    width: 50%;
                    padding: 50px;
                }
                .row{
                    width: 100%;
                }
                p {text-align: center;}
            </style>
            <script src="https://cdn.plot.ly/plotly-2.27.0.min.js" charset="utf-8"></script>
        </head>
        <h1>TreeVal Summary Stats Report</h1>
        <div class="row">
            <div class="boxy">
                <div>
                    <div class="text-uppercase text-primary font-weight-bold text-xs mb-1"><span>Rows of Data</span></div>
                    
                    <div class="text-dark font-weight-bold h5 mb-0"><span> ''' + total_rows + '''</span></div>
                </div>
            </div>
            <div class="boxy">
                <div class="col mr-2">
                    <div class="text-uppercase text-success font-weight-bold text-xs mb-1"><span>Columns of Data</span></div>

                    <div class="text-dark font-weight-bold h5 mb-0"><span>''' + total_cols + '''</span></div>
                </div>
            </div>
        </div>
        <div>
            <h2> General Stats</h2>
            <p>
                ''' + cli + '''
            <p>
        </div>
        <div>
            <h2> Genome Size vs. Runtime </h2>
            <!-- *** Section 1 *** --->
                ''' + a1 + '''
                <!-- *** Section 2 *** --->
                ''' + a2 + '''
                <!-- *** Section 3 *** --->
                ''' + a3 + '''
        </div>
        <div>
            <h2> Clade vs. Runtime </h2>
            <!-- *** Section 1 *** --->
                ''' + b1 + '''
                <!-- *** Section 2 *** --->
                ''' + b2 + '''
                <!-- *** Section 3 *** --->
                ''' + b3 + '''
        </div>
        <div>
            <h2> Family vs. Runtime </h2>
            <!-- *** Section 1 *** --->
                ''' + c1 + '''
                <!-- *** Section 2 *** --->
                ''' + c2 + '''
                <!-- *** Section 3 *** --->
                ''' + c3 + '''
        </div>
        <div>
            <h2> Longread vs. Runtime </h2>
            <!-- *** Section 1 *** --->
                ''' + d1 + '''
                <!-- *** Section 2 *** --->
                ''' + d2 + '''
                <!-- *** Section 3 *** --->
                ''' + d3 + '''
        </div>
        <div>
            <h2> HiC vs. Runtime </h2>
            <!-- *** Section 1 *** --->
                ''' + e1 + '''
                <!-- *** Section 2 *** --->
                ''' + e2 + '''
                <!-- *** Section 3 *** --->
                ''' + e3 + '''
        </div>
        <div>
            <h2> 3D Graphs </h2>
            <!-- *** Section 1 *** --->
                ''' + f1 + '''
                <!-- *** Section 2 *** --->
                ''' + f2 + '''
                <!-- *** Section 3 *** --->
                ''' + f3 + '''
        </div>
        </body>
    </html>
    '''