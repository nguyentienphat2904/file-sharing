import mongoose, { mongo, Schema } from "mongoose";

interface IPeer {
    username: string;
    password: string;
    address: string;
    port: string;
}

const PeerSchema: Schema = new Schema({
    address: { type: String, required: true, unique: true },
    port: { type: String, required: true, unique: true },
    username: { type: String, required: true, unique: true },
    password: { type: String, required: true, unique: true },
}, { versionKey: false });

const PeerModel = mongoose.model<IPeer>('Peer', PeerSchema);

export { PeerModel, IPeer }