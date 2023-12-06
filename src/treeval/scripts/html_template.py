def html_report(cli_output: str, data_shape: list, graph_list: list) -> str:
    HTML_STRING = '''
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

                        <div class="text-dark font-weight-bold h5 mb-0"><span> ''' + str(data_shape[0]) + '''</span></div>
                    </div>
                </div>
                <div class="boxy">
                    <div class="col mr-2">
                        <div class="text-uppercase text-success font-weight-bold text-xs mb-1"><span>Columns of Data</span></div>

                        <div class="text-dark font-weight-bold h5 mb-0"><span>''' + str(data_shape[1]) + '''</span></div>
                    </div>
                </div>
            </div>
            <div>
                <h2> General Stats</h2>
                <p>
                    ''' + cli_ouput + '''
                <p>
            </div>
            <div>
                <h2> mem vs hic data</h2>
                <!-- *** Section 1 *** --->
                    ''' + graph_list[0] + '''
            </div>
            <div>
                <h2> Genome Size vs. Runtime </h2>
                <!-- *** Section 1 *** --->
                    ''' + graph_list[1] + '''
                    <!-- *** Section 2 *** --->
                    ''' + graph_list[2] + '''
                    <!-- *** Section 3 *** --->
                    ''' + graph_list[3] + '''
            </div>
            <div>
                <h2> Clade vs. Runtime </h2>
                <!-- *** Section 1 *** --->
                    ''' + graph_list[4] + '''
                    <!-- *** Section 2 *** --->
                    ''' + graph_list[5] + '''
                    <!-- *** Section 3 *** --->
                    ''' + graph_list[6] + '''
            </div>
            <div>
                <h2> Family vs. Runtime </h2>
                <!-- *** Section 1 *** --->
                    ''' + graph_list[7] + '''
                    <!-- *** Section 2 *** --->
                    ''' + graph_list[8] + '''
                    <!-- *** Section 3 *** --->
                    ''' + graph_list[9] + '''
            </div>
            <div>
                <h2> Longread vs. Runtime </h2>
                <!-- *** Section 1 *** --->
                    ''' + graph_list[10] + '''
                    <!-- *** Section 2 *** --->
                    ''' + graph_list[11] + '''
                    <!-- *** Section 3 *** --->
                    ''' + graph_list[12] + '''
            </div>
            <div>
                <h2> HiC vs. Runtime </h2>
                <!-- *** Section 1 *** --->
                    ''' + graph_list[13] + '''
                    <!-- *** Section 2 *** --->
                    ''' + graph_list[14] + '''
                    <!-- *** Section 3 *** --->
                    ''' + graph_list[15] + '''
            </div>
            <div>
                <h2> 3D Graphs </h2>
                <!-- *** Section 1 *** --->
                    ''' + graph_list[16] + '''
                    <!-- *** Section 2 *** --->
                    ''' + graph_list[17] + '''
                    <!-- *** Section 3 *** --->
                    ''' + graph_list[18] + '''
            </div>
            </body>
        </html>
        '''
    return HTML_STRING