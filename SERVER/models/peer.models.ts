import mongoose, { mongo, Schema } from "mongoose";

interface IPeer {
    username: string;
    password: string;
    address: string;
    port: string;
    role: 'user' | 'admin';
}

const PeerSchema: Schema = new Schema({
    address: { type: String, required: true },
    port: { type: String, required: true },
    username: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    role: { type: String, enum: ['user', 'admin'], default: 'user' }
}, { versionKey: false });

const PeerModel = mongoose.model<IPeer>('Peer', PeerSchema);

export { PeerModel, IPeer }