import { Centrifuge } from 'centrifuge/build/protobuf';
import { decompressSync } from 'fflate';
import {writeFile} from 'node:fs';

const centrifuge = new Centrifuge('wss://notpx.app/connection/websocket');

// GET https://notpx.app/api/v1/users/me
centrifuge.setToken("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaGFubmVscyI6WyJldmVudDptZXNzYWdlIiwicGl4ZWw6bWVzc2FnZSJdLCJleHAiOjE3Mjk2MTEyMTAsInN1YiI6IjcyNjU1MTU2MCJ9.VZ3AjXOcGNVp89ESwNfqEUTlNMOttUW2Bliqc9bl-Uk");

// Allocate Subscription to a channel
// const sub = centrifuge.newSubscription('event:message');
// centrifuge.getSubscription()

// React on 'pixel:message' channel real-time publications
centrifuge.on('publication', function(ctx) {
    console.log('Received data:', ctx.channel, ctx.data);
    const decompressed = decompressSync(ctx.data);
    var string = new TextDecoder().decode(decompressed);
    console.log('Received data:', string);
    writeFile('test.json', string, err => {
        if (err) {
          console.error(err);
        } else {
          // file written successfully
        }
      });

});

centrifuge.on('error', function(ctx) {
    console.log('error', ctx.data);
});

centrifuge.on('connected', function(ctx) {
    console.log('Connected', ctx.transport);
});

centrifuge.on('disconnected', function(ctx) {
    console.log('disconnected', ctx.code, ctx.reason);
});



// Trigger subscribe process
// sub.subscribe();

// Trigger actual connection establishment
centrifuge.connect();


// Keep the process alive for 30 seconds to receive messages
setTimeout(() => {
    console.log('Closing connection after 30 seconds');
    centrifuge.disconnect();
}, 30000);
