import { Component, ViewChild } from '@angular/core';
import { TwitterData } from './model/TwitterData.model';
import { TwitterDataService } from './service/twitter-data.service';
import { ChartConfiguration, ChartOptions, ChartType } from "chart.js";
import { BaseChartDirective } from 'ng2-charts';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {

  time = 'All';
  twitterData : TwitterData[] = []
  dynamicLabels: Date[] = []
  public lineChartLabels:Array<any> = [];

  @ViewChild(BaseChartDirective, { static: true }) chart!: BaseChartDirective; 

  public lineChartData: ChartConfiguration<'line'>['data'] = {
    labels: [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July'
    ],
    datasets: [
      {
        data: [ 65, 59, 80, 81, 56, 55, 40 ],
        label: 'Prices',
        fill: true,
        tension: 0.5,
        borderColor: '#8165ca',
        backgroundColor: 'rgb(114, 82, 196, 0.5)',
      }
    ]
  };

  public lineChartOptions: ChartOptions<'line'> = {
    responsive: true
  };
  public lineChartLegend = false;


  constructor(public twitterDataService: TwitterDataService) {}

  ngOnInit() {
    this.getAll()
  }

  callApi() {
    if(this.time == 'last_day') {
      this.getLast_day()
    }else {
      if(this.time == 'last_hour') {
        this.getLast_hour()
      }
      else {
        if(this.time == 'all') {
          this.getAll()
        }
      }
    }
  }

  getAll()
  {
    this.twitterDataService.getAll()
      .subscribe(data => {
        this.twitterData = data;
        this.lineChartData.datasets[0].data.length = 0
        this.lineChartLabels.length = 0

        this.twitterData.forEach(dat => {
          this.lineChartData.datasets[0].data.push(dat.price)
          this.lineChartLabels.push(dat.timestamp)
        });

        console.log(this.lineChartLabels)

        this.chart.chart!.config.data.labels = this.lineChartLabels
        this.chart.chart?.update()
        
      })
  }

  getLast_hour()
  {
    this.twitterDataService.getLast_Hour()
      .subscribe(data => {
        this.twitterData = data;
        this.lineChartData.datasets[0].data.length = 0
        this.lineChartLabels.length = 0;

        this.twitterData.forEach(dat => {
          this.lineChartData.datasets[0].data.push(dat.price)
          this.lineChartLabels.push(dat.timestamp)
        });
        
        this.chart.chart!.config.data.labels = this.lineChartLabels
        this.chart.chart?.update()
      })
  }

  getLast_day()
  {
    this.twitterDataService.getLast_Day()
      .subscribe(data => {
        this.twitterData = data;
        this.lineChartData.datasets[0].data.length = 0
        this.lineChartLabels.length = 0;

        this.twitterData.forEach(dat => {
          this.lineChartData.datasets[0].data.push(dat.price)
          this.lineChartLabels.push(dat.timestamp)
        });
        console.log(this.lineChartData.datasets[0].data)
        console.log(this.lineChartLabels)

        this.chart.chart!.config.data.labels = this.lineChartLabels
        this.chart.chart?.update()
      })
  }
}
