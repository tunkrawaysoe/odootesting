
import { Component, useState } from "@odoo/owl";

export class Counter extends Component {
    static template = "owl_todo.Counter";

    setup() {
        this.state = useState({ 
            counter1: 0,
            counter2: 0
        });
    }

    // Methods for Counter 1
    inc1 = () => { this.state.counter1++; };
    dec1 = () => { this.state.counter1--; };

    // Methods for Counter 2
    inc2 = () => { this.state.counter2++; };
    dec2 = () => { this.state.counter2--; };
}