import { map } from 'rxjs/operators';



export class TwitterData {
    
    timestamp: Date;
    price: number;

    constructor(timestamp: Date, price: number)
    {
        this.timestamp = timestamp;
        this.price = price;
    }
}