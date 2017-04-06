



$(function () {
        $('#container').highcharts( {
            chart: { zoomType: 'xy' },
            title: { text: 'tests timings' },
            subtitle: { text: 'Click the columns to view Targets/PCRs list' },
            xAxis: [{ categories: dates,
                      labels: { format: '{value}', rotation: 45} }],
            yAxis: [{ // Primary yAxis
                      labels: { format:'{value}', style: { color:'#919191' } },
                      title: { text: 'titre 1 de l axe vertical', style: {color: '#F19191'} } },
                    { // Secondary yAxis
                      title: { text: 'titre 2 de l axe vertical', style: { color: '#4572A7' } },
                      labels: { format: '{value}', style: { color: '#4572A7' } },
                      opposite: true }],
            plotOptions: { column: {cursor: 'pointer',
                                    point: { events: { click: function () {alert("DELIVERY: " + deliveries[this.x] + 
                                                                         " (DATE: "   + dates[this.x] + 
                                                                         " - HOUR: "  + hours[this.x] +
                                                                         ")" );
                                                                         }
                                                     }
                                           }
                                   }
                         },
            tooltip: { shared: true,
                       crosshairs: [true,true],
                       formatter: function() { ind = dates.indexOf(this.x);
                                               yval = this.y;
                                               s = "";
                                               return s;
                                            }

                      },
            legend: { layout: 'vertical', align: 'left', x: 0, verticalAlign: 'top', y: 0, floating: false, backgroundColor: '#F0FFF0' },
            series: [  
                        { name: 'ATT_FL0',  color: '#CCCC00', type: 'spline', data: att_fl0},
                        { name: 'WDF_FL1',  color: '',        type: 'spline', data: wdf_fl1    }  ]
            } );
        });

			