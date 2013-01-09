package org.mitre.poet.model.ws;
import org.mitre.poet.model.InstanceDocument;
import org.mitre.poet.model.lib.ModelCompiler;

import javax.jws.WebMethod;
import javax.jws.WebService;
import javax.xml.ws.Endpoint;

/**
 */
@WebService()
public class ModelCompilerWS {


    @WebMethod
    public String compileModel(String _filter, String _config, String _qa) {

        ModelCompiler compiler = new ModelCompiler();

        InstanceDocument id = compiler.compilerModel(null, null, null);

        return id.xmlText();
    }

    


  public static void main(String[] argv) {
    Object implementor = new ModelCompilerWS ();
    String address = "http://localhost:9000/ModelCompilerWS";
    Endpoint.publish(address, implementor);
  }
}